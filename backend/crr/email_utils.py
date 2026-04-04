import os
import smtplib
from django.core.mail import EmailMessage
from django.conf import settings


def _wrap_email(label, valor, largura=60):
    """Formata 'label: VALOR' com quebra de linha para email."""
    prefixo = f"{label}: "
    valor = str(valor).upper()
    disp = largura - len(prefixo)
    if disp <= 4 or len(valor) <= disp:
        return [prefixo + valor]
    linhas = []
    cont = " " * len(prefixo)
    linhas.append(prefixo + valor[:disp])
    resto = valor[disp:]
    while resto:
        linhas.append(cont + resto[:largura - len(cont)])
        resto = resto[largura - len(cont):]
    return linhas


def gerar_texto_crr(crr):
    """Gera texto formatado do CRR para anexo de email.
    Layout identico ao impresso, com largura adaptada para email."""
    LARG = 60
    DIV = "-" * LARG
    linhas = []

    data = (crr.dataFiscalizacao.strftime('%d/%m/%Y')
            if crr.dataFiscalizacao else '-')
    hora = (crr.horaFiscalizacao.strftime('%H:%M')
            if crr.horaFiscalizacao else '-')

    # Titulo
    linhas.append("COMPROVANTE DE RECOLHIMENTO E REMOCAO - CRR")

    # Identificacao
    linhas.append(DIV)
    linhas.append("IDENTIFICACAO DO CRR")
    linhas.append(DIV)
    linhas += _wrap_email("numero", crr.numeroCrr, LARG)
    linhas += _wrap_email("data", data, LARG)
    linhas += _wrap_email("hora", hora, LARG)

    # Veiculo
    linhas.append(DIV)
    linhas.append("VEICULO")
    linhas.append(DIV)
    v = crr.veiculo.first()
    linhas += _wrap_email("placa", v.placa if v and v.placa else '-', LARG)
    linhas += _wrap_email("chassi", v.chassi if v and v.chassi else '-', LARG)
    linhas += _wrap_email("marca", v.marca if v and v.marca else '-', LARG)
    linhas += _wrap_email("modelo", v.modelo if v and v.modelo else '-', LARG)
    linhas += _wrap_email("cor", v.cor if v and v.cor else '-', LARG)

    # Fiscalizacao
    linhas.append(DIV)
    linhas.append("FISCALIZACAO")
    linhas.append(DIV)
    linhas += _wrap_email("local", crr.localFiscalizacao or '-', LARG)
    linhas += _wrap_email("medida", crr.medidaAdministrativa or '-', LARG)

    aits = [a.ait for a in crr.aits.all()]
    if aits:
        linhas += _wrap_email("AITs", ', '.join(a.upper() for a in aits), LARG)

    enqs = [
        str(e.enquadramento.codigo)
        for e in crr.enquadramentos.all()
        if e.enquadramento
    ]
    if enqs:
        linhas += _wrap_email("enquadr.", ', '.join(enqs), LARG)
        if '00000' in enqs:
            linhas.append("  ART. 279-A")

    # Outros dados
    linhas.append(DIV)
    linhas.append("OUTROS DADOS")
    linhas.append(DIV)
    linhas += _wrap_email("patio", crr.localPatio or '-', LARG)
    linhas += _wrap_email("guincho", crr.placaGuincho or '-', LARG)
    linhas += _wrap_email("encarr.", crr.encarregado or '-', LARG)
    linhas += _wrap_email("agente", crr.matriculaAgente or '-', LARG)

    # Condutor
    linhas.append(DIV)
    linhas.append("CONDUTOR")
    linhas.append(DIV)
    c = crr.condutores.first()
    if c and c.nomeCondutor:
        linhas += _wrap_email("nome", c.nomeCondutor, LARG)
        linhas += _wrap_email("cpf", c.cpfCondutor or '-', LARG)
    else:
        linhas.append("ausente")

    # Observacao
    if crr.observacao:
        linhas.append(DIV)
        linhas.append("OBSERVACAO")
        linhas.append(DIV)
        linhas += _wrap_email("obs.", crr.observacao, LARG)

    # Assinatura condutor
    linhas.append(DIV)
    linhas.append("")
    linhas.append("assinatura do condutor:")
    linhas.append("_" * LARG)

    situacao = crr.situacaoEntrega or ''
    if situacao:
        linhas.append(situacao.upper())

    linhas.append(DIV)
    return "\n".join(linhas)


_CORPO_PATIO = (
    "Prezados,\n\n"
    "Segue em anexo o Comprovante de Recolhimento e Remoção (CRR) da Prefeitura "
    "Municipal de São Sebastião, em razão de descumprimento da legislação de trânsito.\n\n"
    "Atenciosamente,\n"
    "Divisão de Processamento de Multas\n"
    "Secretaria de Segurança Urbana"
)

_CORPO_CONDUTOR = (
    "Prezado condutor/proprietário,\n\n"
    "Por meio deste, segue em anexo o Comprovante de Recolhimento e Remoção (CRR) da "
    "Prefeitura Municipal de São Sebastião, em razão de descumprimento da legislação de trânsito.\n\n"
    "Seguem abaixo as instruções.\n\n"
    "Atenciosamente,\n"
    "Divisão de Processamento de Multas\n"
    "Secretaria de Segurança Urbana\n\n\n"
    "Instruções\n\n"
    "Liberação de Veículo Removido\n"
    "• Instruções para liberação de veículo removido (pdf):\n"
    "  https://www.saosebastiao.sp.gov.br/pdfs/detraf_forms/instrucoes_veiculos_removidos.pdf\n\n"
    "----------------------------------------\n\n"
    "Liberação de Veículo - Bloqueio Digital\n"
    "1. Acesse a plataforma 1DOC pelo link:\n"
    "   https://saosebastiao.1doc.com.br/b.php?pg=wp/wp&itd=5&is=93946&iser=01JGC7AFJV8D2ZFEJV6SQHQJVY\n"
    "2. Faça a identificação usando seu e-mail ou CPF/CNPJ;\n"
    "3. Insira corretamente os dados e documentos solicitados no sistema;\n"
    "4. Junte o Laudo de Vistoria de Infração de Trânsito;\n"
    "5. Confirme a solicitação;\n"
    "6. Após conferência dos documentos e verificação do cumprimento dos requisitos, "
    "será expedido um Ofício de Liberação;\n\n"
    "----------------------------------------\n\n"
    "Protocolo Online\n"
    "1. Prepare a documentação;\n"
    "2. Acessar o link do protocolo on-line;\n"
    "3. Cadastre-se;\n"
    "4. Ao acessar com login e senha clique no lado inferior esquerdo em Incluir Solicitação;\n"
    "5. Escolha a opção: Conversão em Advertência, Defesa Prévia, Recurso JARI - 1ª Instância, "
    "Recurso CETRAN - 2ª Instância ou Indicação de Condutor;\n"
    "6. Digite o Auto de Infração e a placa, depois clique em Localizar Infração;\n"
    "7. Preencha os demais campos e clique em Registrar Protocolo;\n"
    "8. Anexe os documentos pedidos e clique em Enviar Arquivos;\n"
    "9. Pronto! O processo será analisado e você receberá um e-mail confirmando se sua "
    "solicitação foi processada ou se haverá necessidade de regularização."
)


def enviar_email_crr(crr):
    """
    Envia email ao pátio com o CRR como anexo .txt.
    Retorna True em sucesso, False em falha.
    Nunca lança exceção — falha silenciosa para não bloquear a API.
    """
    destino = os.environ.get('EMAIL_PATIO_DESTINO', '')
    if not destino:
        return False

    try:
        v = crr.veiculo.first()
        placa = v.placa.upper() if v and v.placa else 'S/PLACA'
        data = (
            crr.dataFiscalizacao.strftime('%d/%m/%Y')
            if crr.dataFiscalizacao else '-'
        )
        assunto = f"CRR {crr.numeroCrr.upper()} — {placa} — {data}"
        texto = gerar_texto_crr(crr)
        nome_arquivo = f"crr_{crr.numeroCrr}.txt"

        email = EmailMessage(
            subject=assunto,
            body=_CORPO_PATIO,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destino],
        )
        email.attach(nome_arquivo, texto, 'text/plain')
        email.send(fail_silently=False)
        return True

    except Exception:
        return False


def enviar_email_condutor(crr, email_condutor):
    """
    Envia email ao condutor com o CRR como anexo .txt.
    Retorna (True, '') em sucesso, (False, 'mensagem') em falha.
    """
    if not email_condutor:
        return False, 'Email do condutor não informado'

    try:
        v = crr.veiculo.first()
        placa = v.placa.upper() if v and v.placa else 'S/PLACA'
        data = (
            crr.dataFiscalizacao.strftime('%d/%m/%Y')
            if crr.dataFiscalizacao else '-'
        )
        assunto = f"CRR {crr.numeroCrr.upper()} — {placa} — {data}"
        texto = gerar_texto_crr(crr)
        nome_arquivo = f"crr_{crr.numeroCrr}.txt"

        email = EmailMessage(
            subject=assunto,
            body=_CORPO_CONDUTOR,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_condutor],
        )
        email.attach(nome_arquivo, texto, 'text/plain')
        connection = email.get_connection()
        connection.timeout = 20
        email.connection = connection
        email.send(fail_silently=False)
        return True, ''

    except smtplib.SMTPException as e:
        return False, f'Erro SMTP: {str(e)}'
    except Exception as e:
        return False, str(e)

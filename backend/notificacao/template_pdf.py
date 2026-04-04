from reportlab.lib.units import cm
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
import requests
from io import BytesIO
from reportlab.lib.utils import ImageReader


def render_notificacao_template(c, notificacao, width, height):

    def limitar_texto(texto, limite):
        return texto if len(texto) <= limite else texto[:limite]
    
    largura, altura = LETTER 


    crr = notificacao.crr
    aits = notificacao.crr.aits.all()

    primeiro_ait = aits[0].ait if len(aits) > 0 else ""
    segundo_ait = aits[1].ait if len(aits) > 1 else ""  
    terceiro_ait = aits[2].ait if len(aits) > 2 else ""  
    quarto_ait = aits[3].ait if len(aits) > 3 else ""  

    imagens = list(notificacao.crr.imagens.all())
    imagemVeiculo = None

    if imagens:
        imagem_obj = imagens[0]

        try:
            if imagem_obj.imagem:  # upload local
                imagemVeiculo = ImageReader(imagem_obj.imagem.path)
            elif imagem_obj.url:  # imagem via URL externa (S3)
                response = requests.get(imagem_obj.url)
                if response.status_code == 200:
                    imagem_bytes = BytesIO(response.content)
                    imagemVeiculo = ImageReader(imagem_bytes)
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")

    condutores = list(notificacao.crr.condutores.all())
    
    cnh =  condutores[0].cnh  if len(condutores) > 0 else "—"
    ufCnh =  condutores[0].ufCnh  if len(condutores) > 0 else "—"
    cpfCondutor =  condutores[0].cpfCondutor  if len(condutores) > 0 else "—" 
    nomeCondutor =  condutores[0].nomeCondutor  if len(condutores) > 0 else "—"

    veiculo = list(notificacao.crr.veiculo.all())
    
    placa =  veiculo[0].placa  if len(veiculo) > 0 else "—"
    chassi =  veiculo[0].chassi  if len(veiculo) > 0 else "—"
    marca =  veiculo[0].marca  if len(veiculo) > 0 else "—" 
    modelo =  veiculo[0].modelo  if len(veiculo) > 0 else "—"
    cor =  veiculo[0].cor  if len(veiculo) > 0 else "—"
    especie =  veiculo[0].especie  if len(veiculo) > 0 else "—"
    categoria =  veiculo[0].categoria  if len(veiculo) > 0 else "—"
    ufVeiculo =  veiculo[0].ufVeiculo  if len(veiculo) > 0 else "—"
    municipioVeiculo =  veiculo[0].municipioVeiculo  if len(veiculo) > 0 else "—"
   
    enquadramentos = list(notificacao.crr.enquadramentos.all())

    primeiro_enquadramento = enquadramentos[0].enquadramento.codigo  if len(enquadramentos) > 0 else "—"
    segundo_enquadramento =  enquadramentos[1].enquadramento.codigo  if len(enquadramentos) > 1 else "-"
    terceiro_enquadramento = enquadramentos[2].enquadramento.codigo  if len(enquadramentos) > 2 else "-"
    quarto_enquadramento =   enquadramentos[3].enquadramento.codigo if len(enquadramentos) > 3 else "-"

    primeiro_amparo_legal = enquadramentos[0].enquadramento.amparo_legal  if len(enquadramentos) > 0 else "—"
    
    primeiro_descricao_infracao = enquadramentos[0].enquadramento.descricao_infracao  if len(enquadramentos) > 0 else "—"

    arrendatarios = list(notificacao.crr.arrendatarios.all())
    nome_arrendatario = arrendatarios[0].arrendatario.nome_arrendatario  if len(arrendatarios) > 0 else "—"


    # Configuração da página (agora usando LETTER)
    largura, altura = LETTER  # Dimensões: 8.5 x 11 polegadas
   
    

     # Inserir uma imagem (exemplo: logo da prefeitura)
    try:
        imagem = ImageReader("static/brasao.jpg")  # Substitua pelo caminho da sua imagem
        c.drawImage(imagem, 2 * cm, altura - 6 * cm, width=2 * cm, height=3 * cm, preserveAspectRatio=True)
    except Exception as e:
        print(f"Erro ao carregar a imagem: {e}")
    
    # Título principal
    c.setFont("Helvetica-Bold", 14)
    c.drawString(6 * cm, altura - 3 * cm, "PREFEITURA MUNICIPAL DE SÃO SEBASTIÃO")

    c.setFont("Helvetica", 12)
    c.drawString(7 * cm, altura - 4 * cm, "SECRETARIA DE SEGURANÇA URBANA")

     # Linha horizontal acima de notificação de remoção de veículos ao pátio
    c.line(4 * cm, altura - 5.0 * cm, largura - 2 * cm, altura - 5.0 * cm)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(7 * cm, altura - 5.4 * cm, "NOTIFICAÇÃO DE REMOÇÃO DE VEÍCULOS AO PÁTIO")
    
    # Linha horizontal abaixo de notificação de autuação por infração de trânsito
    c.line(4 * cm, altura - 5.5 * cm, largura - 2 * cm, altura - 5.5 * cm)
    
    # Identificação da Autuação
    c.setFont("Helvetica-Bold", 10)
    c.drawString(8 * cm, altura - 5.9 * cm, "Identificação da Autuação")
    # 1ª Linha horizontal abaixo de identificação da autuação
    c.line(2 * cm, altura - 6.1 * cm, largura - 2 * cm, altura - 6.1 * cm)
    # 2ª Linha horizontal abaixo de identificação da autuação
    c.line(2 * cm, altura - 7 * cm, largura - 2 * cm, altura - 7 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, altura - 6.4 * cm, "Código órgão Autuador")
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, altura - 6.9 * cm,  "271150")
     # Barra vertical
    c.line(5.8* cm, altura - 6.1 * cm, 5.8 * cm, altura - 7 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(6 * cm, altura - 6.4 * cm, "N° C.R.R.") #\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    c.drawString(6 * cm, altura - 6.9 * cm, str(crr.numeroCrr)) #\\\\\\\\\\\\\\\\
    # Barra vertical em frente auto de infração
    c.line(9* cm, altura - 6.1 * cm, 9 * cm, altura - 7 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(9.5 * cm, altura - 6.4 * cm, "Data da Postagem:") #\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    data_postagem = notificacao.data_postagem.strftime('%d/%m/%Y')
    c.drawString(9.5 * cm, altura - 6.9 * cm, data_postagem) #\\\\\\\\\\\\\\\
    # Barra vertical em frente data de postagem 
    c.line(12.7* cm, altura - 6.1 * cm, 12.7 * cm, altura - 7 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(13 * cm, altura - 6.4 * cm, "Data Emissão:") #\\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    data_emissao = notificacao.data_emissao.strftime('%d/%m/%Y')
    c.drawString(13 * cm, altura - 6.9 * cm, f"{data_emissao}")
    # Barra vertical em frente data emissão
    c.line(15.7* cm, altura - 6.1 * cm, 15.7 * cm, altura - 7 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(16.5 * cm, altura - 6.4 * cm, "Numero Controle:")
    c.setFont("Helvetica", 10)
    c.drawString(16.5 * cm, altura - 6.9 * cm, str(notificacao.numero_controle))
    
    
    # Linha horizontal abaixo da identificação do veículo
    c.line(2 * cm, altura - 7.7 * cm, largura - 2 * cm, altura - 7.7 * cm)
    # Identificação do Veículo
    c.setFont("Helvetica-Bold", 10)
    c.drawString(8 * cm, altura - 7.5 * cm, "Identificação do Veículo")
    
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, altura - 8 * cm, "Placa / Chassi:") #\\\\\\\\\\\\\\\\\\\\\\\
     # Barra vertical
    c.line(6.3* cm, altura - 7.7 * cm, 6.3* cm, altura - 8.6 * cm)
    c.setFont("Helvetica", 10)
    sem_identificado = "SEM IDENTIFICAÇÃO"
    placa_chassi = (placa or chassi or sem_identificado).upper()
    c.drawString(2 * cm, altura - 8.5 * cm, str(placa_chassi)) #\\\\\\\\\\\\\\\\\\\\\\\\\\

    
    c.setFont("Helvetica", 8)
    c.drawString(6.5 * cm, altura - 8 * cm, "Marca / Modelo:") #\\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    marca_limite = limitar_texto(marca.upper(), 7) 
    modelo_limite = limitar_texto(modelo.upper(), 7) 
    c.drawString(6.5 * cm, altura - 8.5 * cm, f"{marca_limite}/{modelo_limite}") #\\\\\\\\\\\\\\\
    # Barra vertical
    c.line(9.8* cm, altura - 7.7 * cm, 9.8 * cm, altura - 8.6 * cm)

   
    c.setFont("Helvetica", 8)
    c.drawString(9.9 * cm, altura - 8 * cm, "Espécie:") #\\\\\\\\\\\\\\\\\\\\\\\\\
    # Barra vertical
    c.setFont("Helvetica", 10)
    c.drawString(9.9 * cm, altura - 8.5 * cm, especie.upper()) #\\\\\\\\\\\\\\\\\\\\\
    c.line(12.3* cm, altura - 7.7 * cm, 12.3 * cm, altura - 8.6 * cm)


    c.setFont("Helvetica", 8)
    c.drawString(12.4 * cm, altura - 8 * cm, "Categoria:") #\\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    c.drawString(12.4 * cm, altura - 8.5 * cm, categoria.upper()) #\\\\\\\\\\\\\\\
     # Barra vertical
    c.line(14.7* cm, altura - 7.7 * cm, 14.7 * cm, altura - 8.6 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(14.8 * cm, altura - 8 * cm, "Município / UF:") #\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    municipio_limite = limitar_texto(municipioVeiculo.upper(), 20)
    c.drawString(14.8 * cm, altura - 8.5 * cm, f"{municipio_limite}/{ufVeiculo.upper()}")
    
   
    
    # Linha horizontal acima de identificação do local da infração
    c.line(2 * cm, altura - 8.6 * cm, largura - 2 * cm, altura - 8.6 * cm)
     # Local da Infração
    c.setFont("Helvetica-Bold", 10)
    c.drawString(8 * cm, altura - 9 * cm, "Identificação do Local da remoção")
        # Linha horizontal abaixo de identificação do local da infração
    c.line(2 * cm, altura - 9.1 * cm, largura - 2 * cm, altura - 9.1 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, altura - 9.4 * cm, "Local da remoção") #\\\\\\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    local_limite = limitar_texto(crr.localFiscalizacao.upper(), 100)
    c.drawString(2 * cm, altura - 9.9 * cm, local_limite) # \\\\\\\\\\\\\\\\\\\\\\\\
        # Linha horizontal acima de local da infração
    c.line(2 * cm, altura - 10 * cm, largura - 2 * cm, altura - 10 * cm)

 # Linha horizontal acima de "Município / UF / Código:"
    c.line(2 * cm, altura - 11 * cm, largura - 9.6 * cm, altura - 11 * cm)
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, altura - 11.3* cm, "Município / UF / Código:")
    # Barra vertical
    c.line(6.9* cm, altura - 11 * cm, 6.9 * cm, altura - 11.8 * cm)

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, altura - 11.8 * cm, "SÃO SEBASTIÃO / SP / 7115")

    c.setFont("Helvetica", 8)
    c.drawString(7.1 * cm, altura - 11.3 * cm, "Data da remoção:") #\\\\\\\\\\\\\\
    # Barra vertical
    c.line(9.5 * cm, altura - 11 * cm, 9.5 * cm, altura - 11.9 * cm)

    c.setFont("Helvetica", 10)
    dataFiscalizacao = crr.dataFiscalizacao.strftime('%d/%m/%Y')
    c.drawString(7.1 * cm, altura - 11.8 * cm, dataFiscalizacao) #\\\\\\\\\\\\\\\\\\\\

    c.setFont("Helvetica", 8)
    c.drawString(9.7 * cm, altura - 11.3 * cm, "Hora da remoção:") #\\\\\\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    c.drawString(9.7 * cm, altura - 11.8 * cm, str(crr.horaFiscalizacao))  #\\\\\\\\\\\\\\\\\\\\\\\

    # retangulo para imagem
        #   (x  , y,   largura, altura, stroke=1, fill=0)
    c.rect(12*cm, 12.53*cm, 7.5*cm, 4.41*cm , stroke=1, fill=0)

    # Imagem Brasão
    #imagem =  notificacao.crr.imagens.first() if notificacao.crr.imagens.exists() else None 
    try:
        c.drawImage(imagemVeiculo, 12.1 * cm, altura - 15.4 * cm, width=7.3 * cm, height=4.4 * cm, preserveAspectRatio=True)
    except Exception as e:
        print(f"Erro ao carregar a imagem: {e}")

    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, altura - 10.3 * cm, "Observação:") #\\\\\\\\\\\\\\\\\\\\\\\\
    observacao_limite = limitar_texto(crr.observacao.upper(), 98) +'...'
    c.drawString(2 * cm, altura - 10.8 * cm, str(observacao_limite))
    
    # Definir estilos de texto
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]

    
    # Linha horizontal acima da tipificação da infração
    c.line(2 * cm, altura - 11.9 * cm, largura - 9.6 * cm, altura - 11.9 * cm)

    # Tipificação da Infração
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5.5 * cm, altura - 12.35 * cm, "Tipificação da Infração")
    # Linha horizontal abaixo da tipificação da infração
    c.line(2 * cm, altura - 12.5 * cm, largura - 9.6 * cm, altura - 12.5 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, altura - 12.8 * cm, "Descrição da Infração:")
    # Barra vertical
    c.line(6.8* cm, altura - 12.5 * cm, 6.8 * cm, altura - 14.7 * cm)

    # ------ DESCRIÇÃO DA INFRAÇÃO ------ #\\\\\\\\\\\\\\\\\\\\\\\\\\
    # ------ DESCRIÇÃO DA INFRAÇÃO ------ #\\\\\\\\\\\\\\\\\\\\\\\\\\

    # Primeiro defina a função auxiliar para quebrar o texto
    def quebrar_texto_em_linhas(texto, limite_por_linha=50, max_linhas=3):
        """Quebra um texto longo em múltiplas linhas com limite de caracteres"""
        if not texto:
            return []
        
        texto_limitado = texto[:limite_por_linha * max_linhas]
        palavras = texto_limitado.split()
        linhas = []
        linha_atual = ""
        
        for palavra in palavras:
            if len(linha_atual) + len(palavra) + 1 <= limite_por_linha:
                linha_atual += (" " if linha_atual else "") + palavra
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
                if len(linhas) >= max_linhas:
                    break
        
        if linha_atual and len(linhas) < max_linhas:
            linhas.append(linha_atual)
        
        return linhas

    # Agora defina a função principal para desenhar
    def desenhar_texto_multilinha(c, texto, x, y, limite_por_linha=50, max_linhas=3, espacamento=12):
        """Desenha texto com múltiplas linhas no PDF"""
        linhas = quebrar_texto_em_linhas(texto, limite_por_linha, max_linhas)
        
        for i, linha in enumerate(linhas):
            c.drawString(x, y - (i * espacamento), linha)
        
        if len(texto) > limite_por_linha * max_linhas:
            c.drawString(x, y - (len(linhas) * espacamento),f"...")

    # Configurações e renderização do texto
    texto_descricao = str(primeiro_descricao_infracao)
    desenhar_texto_multilinha(
        c,
        texto_descricao,
        x=2 * cm,
        y=altura - 13.2 * cm,
        limite_por_linha=35,
        max_linhas=4,
        espacamento=11
    )

    
    c.setFont("Helvetica", 8)
    c.drawString(7 * cm, altura - 12.8 * cm, "Enquadramento:")
    # Barra vertical
    c.line(9.3* cm, altura - 12.5 * cm, 9.3 * cm, altura - 14.7 * cm)

    c.setFont("Helvetica", 10)
    c.drawString(7 * cm, altura - 13.3 * cm,str(primeiro_enquadramento))
    c.drawString(7 * cm, altura - 13.7 * cm, str(segundo_enquadramento))
    c.drawString(7 * cm, altura - 14.1 * cm, str(terceiro_enquadramento))
    c.drawString(7 * cm, altura - 14.5 * cm, str(quarto_enquadramento))

    c.setFont("Helvetica", 8)
    c.drawString(9.5* cm, altura - 12.8 * cm, "Auto de infração:") 
    c.setFont("Helvetica", 10)
    c.drawString(9.5* cm, altura - 13.3 * cm, f"{primeiro_ait.upper()}") 
    c.drawString(9.5* cm, altura - 13.7 * cm, f"{segundo_ait.upper()}") 
    c.drawString(9.5* cm, altura - 14.1 * cm, f"{terceiro_ait.upper()}")
    c.drawString(9.5* cm, altura - 14.5 * cm, f"{quarto_ait.upper()}")

     # Linha horizontal acima de Amparo Legal
    c.line(2 * cm, altura - 14.7 * cm, largura - 9.6 * cm, altura - 14.7 * cm)
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, altura - 15 * cm, "Amparo Legal:") # \\\\\\\\\\\\\\\\\\
    # Barra vertical
    c.line(5* cm, altura - 14.7 * cm, 5 * cm, altura - 15.5* cm)

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, altura - 15.4* cm, str(primeiro_amparo_legal)) #Art. 279-A C.T.B. \\\\\\\\

    c.setFont("Helvetica", 8)
    c.drawString(6 * cm, altura - 15 * cm, "Identificação da Autoridade/Agente Autuador:") # \\\\\\\\\
    c.setFont("Helvetica", 10)
    c.drawString(6 * cm, altura - 15.4 * cm, str(crr.matriculaAgente)) # \\\\\\\\\\\\\\\\\\
    
    
    # Linha horizontal acima da identificação de condutor 
    c.line(2 * cm, altura - 15.5 * cm, largura - 2 * cm, altura - 15.5 * cm)
    # Identificação do Condutor
    c.setFont("Helvetica-Bold", 10)
    c.drawString(8 * cm, altura - 15.9 * cm, "Identificação do Condutor")
    # Linha horizontal abaixo de indentificação de condutor
    c.line(2 * cm, altura - 16 * cm, largura - 2 * cm, altura - 16 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, altura - 16.3 * cm, "Nº Habilitação do Condutor:") 
    # Barra vertical
    c.line(5.7* cm, altura - 16 * cm, 5.7 * cm, altura - 16.8 * cm)

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, altura - 16.7 * cm,  cnh) 

     #Linha horizontal abaixo da habilitação do condutor
    c.line(2 * cm, altura - 16.8 * cm, largura - 2 * cm, altura - 16.8 * cm)

    c.setFont("Helvetica", 8)
    c.drawString(6 * cm, altura - 16.3 * cm, "UF:") #\\\\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    c.drawString(6 * cm, altura - 16.7 * cm, str(ufCnh).upper()) #\\\\\\\\\\\\\

    c.setFont("Helvetica", 8)
    c.drawString(7 * cm, altura - 16.3 * cm, "CPF:") # \\\\\\\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    c.drawString(7 * cm, altura - 16.7 * cm, cpfCondutor) #\\\\\\\\\\\\\\\\\\\\\\\\\
    

    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, altura - 17.1 * cm, "Nome:") # \\\\\\\\\\\\\\\\\
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, altura - 17.5 * cm, str(nomeCondutor).upper()) # \\\\\\\\\\\\\\\\\\\\\\\
    #Linha horizontal abaixo de NOME
    c.line(2 * cm, altura - 17.6 * cm, largura - 2 * cm, altura - 17.6 * cm)
    
    
    
    # Informações Importantes
    c.setFont("Helvetica-Bold", 10)
    c.drawString(8 * cm, altura - 18 * cm, "Informações Importantes")
    c.setFont("Helvetica", 10) 
    c.drawString(2 * cm, altura - 18.4 * cm, "Veículo não reclamado (solicitado) em até 60 dias após a remoção poderá ser leiloado. (Art. 328 C.T.B.)")
    c.setFont("Helvetica", 10)
    data_prazo_leilao = notificacao.prazo_leilao.strftime('%d/%m/%Y')
    c.drawString(2 * cm, altura - 18.9 * cm, f'Apto para leilão a partir de: {data_prazo_leilao}') #\\\\\\\\\\\\
    c.drawString(2 * cm, altura - 19.4 * cm, "Nome do pátio: Patio E Guincho Universal LTDA")
    c.drawString(2 * cm, altura - 19.9 * cm, f'Local do pátio: {crr.localPatio.upper()}')
    #"Local do pátio: Rua Bolivia, Nº202, Jaraguá - São Sebastião/SP - CEP: 11600-748"
    # Linha horizontal abaixo da Informações Importantes da Notificação de Autuação
    c.line(2 * cm, altura - 20.4 * cm, largura - 2 * cm, altura - 20.4* cm)
    
    c.setFont("Helvetica-Bold", 10)   
    c.drawString(8 * cm, altura - 20.8 * cm, "OUTRAS INFORMAÇÕES")
    # Linha horizontal abaixo de "OUTRAS INFORMAÇÕES"
    c.line(2 * cm, altura - 20.9 * cm, largura - 2 * cm, altura - 20.9 * cm)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(3 * cm, altura - 22 * cm, "SOLICITE A RETIRADA DO VEÍCULO JUNTO À DIVISÃO DE PROCESSAMENTO DE MULTAS")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(3 * cm, altura - 22.5 * cm, "Telefone: (12) 3892-6180 / 3892-1540 ou através do e-mail: transito@saosebasitao.sp.gov.br")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(3 * cm, altura - 23.5 * cm, "PROTOCOLO DE LIBERAÇÃO DE VEÍCULOS REMOVIDOS ATRAVÉS DO 1DOC:")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(3 * cm, altura - 24 * cm, "https://saosebastiao.1doc.com.br/b.php?pg=o/wp")
    
   
    
     ######################### PRÓXIMA PÁGINA #################################
    c.showPage()
 ########################### Rodapé#####################################
   

# Destinatário
    # retangulo destinatário
        #   (x  , y,   largura, altura, stroke=1, fill=0)
    c.rect(2*cm, 25*cm, 17*cm, 3.5*cm , stroke=1, fill=0)
    c.setFont("Helvetica", 8)
    c.drawString(2.2 * cm, 28.2 * cm, "DESTINATÁRIO")
    c.setFont("Helvetica", 10)
    c.drawString(2.2 * cm, 27.7 * cm, notificacao.destinatario.upper())
    
    c.drawString(2.2 * cm, 26.6 * cm, f"{notificacao.endereco.upper()}, {notificacao.numero.upper()}    {notificacao.complemento.upper()}  -   {notificacao.bairro.upper()}")
    c.drawString(2.2 * cm, 26.1 * cm,f"{notificacao.cep.upper()}           {notificacao.cidade_destinatario.upper()} / {notificacao.uf_destinatario.upper()}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(6 * cm, 25.15 * cm, "NOTIFICAÇÃO DE REMOÇÃO DE VEÍCULO")
    # Linha horizontal acima de NOTIFCAÇÃO DE REMOÇÃO DE VEÍCULO"
    c.line(2 * cm, altura - 2.3 * cm, largura - 2.6 * cm, altura - 2.3 * cm)

    # Remetente
    c.setFont("Helvetica-Bold",8)
    c.drawString(8.5 * cm, 23.9 * cm, "REMETENTE")
    c.drawString(8.5 * cm, 23.6 * cm, "PREFEITURA MUNICIPAL DE SÃO SEBASTIÃO")
    c.drawString(8.5 * cm, 23.3 * cm, "SECRETARIA DE SEGURANÇA URBANA")
    c.drawString(8.5 * cm, 23 * cm, "RUA AMAZONAS N°84 - INDUSTRIAL")
    c.drawString(8.5 * cm, 22.7 * cm, "CEP: 11609-509        SÃO SEBASTIÃO / SP")

    c.setDash(3, 3)  # Define o padrão de tracejado (3 pontos desenhados, 3 pontos vazios)
    c.line(2 * cm, altura - 5.8 * cm, largura - 2 * cm, altura - 5.8 * cm)  # Desenha a linha 

 # Remetente
    c.setFont("Helvetica-Bold",12)
    c.drawString(7 * cm, 20.3 * cm, "Desacelere. Seu bem maior é a vida.")

# Imagem do trânsito 2ª pagina (VERSO) 
    try:
        imagem = ImageReader("static/verso.jpeg")  # Substitua pelo caminho da sua imagem
        c.drawImage(imagem, 1 * cm, altura - 16.2* cm, width=19* cm, height=10 * cm, preserveAspectRatio=True)
    except Exception as e:
        print(f"Erro ao carregar a imagem: {e}") 
#____________________________________________________________________________________#

    c.setDash(3, 3)  # Define o padrão de tracejado (3 pontos desenhados, 3 pontos vazios)
    c.line(2 * cm, altura - 16.9 * cm, largura - 2 * cm, altura - 16.9 * cm)  # Desenha a linha
    c.setDash()
# Rodapé da 2ª pagina 
 # Imagem do rodapé 2ª pagina 
    try:
        imagem = ImageReader("static/cabeçalho.jpg")  # Substitua pelo caminho da sua imagem
        c.drawImage(imagem, 2 * cm, altura - 25.5 * cm, width=17 * cm, height=13.5 * cm, preserveAspectRatio=True)
    except Exception as e:
        print(f"Erro ao carregar a imagem: {e}")

    # retangulo destinatário
        #   (x  , y,   largura, altura, stroke=1, fill=1)
    c.rect(3*cm, 3*cm, 15*cm, 3*cm , stroke=1, fill=0)
    # Destinatário 2ª pagina
    c.setFont("Helvetica", 8)
    c.drawString(3.2 * cm, 5.6 * cm, "DESTINATÁRIO")
    c.setFont("Helvetica", 10)
    c.drawString(3.2 * cm, 5 * cm, notificacao.destinatario.upper())
    
    c.drawString(3.2 * cm, 4 * cm,f"{notificacao.endereco.upper()}, {notificacao.numero.upper()} - {notificacao.complemento.upper()} - {notificacao.bairro.upper()}")
    c.drawString(3.2 * cm, 3.5 * cm, f"{notificacao.cep.upper()}              {notificacao.cidade_destinatario.upper()} / {notificacao.uf_destinatario.upper()}")
    
    
    print("PDF '' criado com sucesso!")



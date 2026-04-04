document.addEventListener('DOMContentLoaded', function () {

    // === PLACEHOLDERS DINÂMICOS ===
    const placeholderMap = {
        placa: "Placa",
        chassi: "Chassi",
        matriculaAgente: "Somente números",
        dataFiscalizacao: "dd/mm/aaaa",
        horaFiscalizacao: "hh:mm",
        localPatio: "Local do Pátio",
        placaGuincho: "Placa do Guincho",
        encarregado: "Encarregado do Guincho",
        ait: "A43-0123456",
        enquadramento: "Somente números",
        cnpj_arrendatario: "00.000.000/0000-00",
        numero_arrendatario: "Somente números",
        cep_arrendatario: "00000-000",
        data_emissao: "dd/mm/aaaa",
        data_postagem: "dd/mm/aaaa",
        numero_controle: "Somente números",
        prazo_leilao: "dd/mm/aaaa",
        numero: "Somente números",
        cep: "00000-000",
        cnh: "Somente números",
        cpfCondutor: "000.000.000-00",
        searchbar: "Digite a placa / CRR"
    };

    Object.entries(placeholderMap).forEach(([key, value]) => {
        document.querySelectorAll(`input[id$="${key}"]`).forEach(field => {
            field.setAttribute('placeholder', value);
        });
    });

    // === FUNÇÕES DE MÁSCARA ===
    const masks = {
        cpf: v => v.replace(/\D/g, '').replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d{1,2})$/, '$1-$2'),
        cnpj: v => v.replace(/\D/g, '').replace(/(\d{2})(\d)/, "$1.$2")
            .replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d)/, "$1/$2")
            .replace(/(\d{4})(\d{1,2})$/, "$1-$2"),
        cep: v => v.replace(/\D/g, '').replace(/(\d{5})(\d)/, "$1-$2"),
        date: v => v.replace(/\D/g, '').replace(/(\d{2})(\d)/, "$1/$2").replace(/(\d{2})(\d)/, "$1/$2"),
        time: v => v.replace(/\D/g, '').replace(/(\d{2})(\d)/, "$1:$2"),
        ait: v => v.replace(/\W/g, '').replace(/^([A-Za-z])(\d{2})(\d+)/, '$1$2-$3').toUpperCase(),
        placa: v => v.replace(/[^A-Za-z0-9]/g, '').toUpperCase(),
        onlyNumbers: v => v.replace(/\D/g, '')
    };

    const maskMap = {
        numeroCrr: masks.onlyNumbers,
        placa: masks.placa,
        matriculaAgente: masks.onlyNumbers,
        dataFiscalizacao: masks.date,
        horaFiscalizacao: masks.time,
        placaGuincho: masks.placa,
        cnpj_arrendatario: masks.cnpj,
        cep_arrendatario: masks.cep,
        cep: masks.cep,
        numero_arrendatario: masks.onlyNumbers,
        numero: masks.onlyNumbers,
        ait: masks.ait,
        enquadramento: masks.onlyNumbers,
        data_emissao: masks.date,
        data_postagem: masks.date,
        prazo_leilao: masks.date,
        numero_controle: masks.onlyNumbers,
        cnh: masks.onlyNumbers,
        cpfCondutor: masks.cpf
    };

    function aplicarMascaras(contexto = document) {
        Object.entries(maskMap).forEach(([key, maskFn]) => {
            contexto.querySelectorAll(`input[id$="${key}"]`).forEach(input => {
                input.addEventListener('input', e => {
                    e.target.value = maskFn(e.target.value);
                });
            });
        });
    }

    aplicarMascaras();

    // Reaplica após adicionar um novo formulário inline
    document.body.addEventListener('click', function (e) {
        if (e.target.closest('.add-row')) {
            setTimeout(() => aplicarMascaras(document), 200);
        }
    });

    // Também escuta eventos de inserção de node dinâmico (Django >= 4 usa isso)
    const observer = new MutationObserver(mutations => {
        mutations.forEach(m => {
            m.addedNodes.forEach(n => {
                if (n.nodeType === 1 && n.querySelectorAll) {
                    aplicarMascaras(n);
                }
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // === VALIDAÇÃO FINAL E NORMALIZAÇÃO AO ENVIAR ===
    document.querySelectorAll('form').forEach(form => {
        if (
            form.querySelector('#id_placa') ||
            form.querySelector('#id_numero_controle') ||
            form.querySelector('#id_cpfCondutor')
        ) {
            form.addEventListener('submit', function (e) {
                const requiredLengths = {
                    cpfCondutor: 11,
                    cnpj_arrendatario: 14,
                    cep_arrendatario: 8,
                    cep: 8
                };

                const errors = [];

                Object.entries(requiredLengths).forEach(([id, length]) => {
                    form.querySelectorAll(`input[id$="${id}"]`).forEach(field => {
                        const value = field.value.replace(/\D/g, '');
                        if (value.length !== length) {
                            errors.push(`${field.name || id} deve conter ${length} dígitos.`);
                        }
                    });
                });

                if (errors.length) {
                    e.preventDefault();
                    alert(errors.join('\n'));
                    return false;
                }

                // Normalização
                form.querySelectorAll('input').forEach(field => {
                    const id = field.id || '';
                    const isNumberField = ['cpfCondutor', 'cnpj', 'cep', 'numero', 'enquadramento', 'matriculaAgente', 'cnh'].some(k => id.includes(k));
                    field.value = isNumberField ? field.value.replace(/\D/g, '') : field.value.toLowerCase();
                });
            });
        }
    });

});

/*
╔══════════════════════════════════════════╗
║         INICIALIZAÇÃO DE RELATÓRIOS       ║
╠══════════════════════════════════════════╣
║► [1] Carregamento de Dados                ║
║► [2] Renderização de Tabelas              ║
║► [3] Tratamento de Erros                  ║
╚══════════════════════════════════════════╝
*/

document.addEventListener('DOMContentLoaded', async () => {
    try {
        // ╔══════════════════════════════════════════╗
        // ║          [1] CARREGAMENTO DE DADOS       ║
        // ╚══════════════════════════════════════════╝
        const [culturas, movimentacoes] = await Promise.all([
            carregarDados('culturas'),
            carregarDados('movimentacoes')
        ]);

        // ╔══════════════════════════════════════════╗
        // ║       [2] RENDERIZAÇÃO DE TABELAS        ║
        // ╚══════════════════════════════════════════╝
        const tabelaCulturas = document.querySelector('#tabela-culturas tbody');
        const tabelaMovimentacoes = document.querySelector('#tabela-movimentacoes tbody');

        // [2.1] Tabela de Culturas
        culturas.forEach(cultura => {
            tabelaCulturas.innerHTML += `
                <tr class="dados-cultura">
                    <td>${cultura.id}</td>
                    <td>${cultura.nome}</td>
                    <td>${cultura.ciclo} dias</td>
                    <td>${formatarData(cultura.data_registro)}</td>
                </tr>
            `;
        });

        // [2.2] Tabela de Movimentações
        movimentacoes.forEach(mov => {
            tabelaMovimentacoes.innerHTML += `
                <tr class="dados-movimentacao">
                    <td>${mov.id}</td>
                    <td>${mov.produto}</td>
                    <td class="setor-${mov.setor.toLowerCase()}">${mov.setor}</td>
                    <td>${formatarData(mov.data)}</td>
                </tr>
            `;
        });

        console.log('✅ Relatórios carregados com sucesso');

    } catch (error) {
        // ╔══════════════════════════════════════════╗
        // ║          [3] TRATAMENTO DE ERROS         ║
        // ╚══════════════════════════════════════════╝
        console.error('❌ Erro ao carregar relatórios:', error);
        mostrarAlerta('Erro ao carregar dados. Tente recarregar a página.', 'danger');
    }
});

/*
╔══════════════════════════════════════════╗
║             FUNÇÕES AUXILIARES           ║
╚══════════════════════════════════════════╝
*/

// Formatação de data (DD/MM/AAAA)
function formatarData(dataString) {
    return new Date(dataString).toLocaleDateString('pt-BR');
}

// Exemplo de função de alerta
function mostrarAlerta(mensagem, tipo) {
    const container = document.createElement('div');
    container.innerHTML = `
        <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
            ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.body.prepend(container);
}
/*
╔══════════════════════════════════════════╗
║         CONTROLE DE MENU MOBILE & API     ║
╠══════════════════════════════════════════╣
║                [1] SUBMENU               ║
║                [2] EVENTOS               ║
║                [3] API                   ║
╚══════════════════════════════════════════╝
*/

// ╔══════════════════════════════════════════╗
// ║                 [1] SUBMENU              ║
// ╚══════════════════════════════════════════╝
function toggleSubmenu() {
    const submenus = document.querySelectorAll('.submenu');
    submenus.forEach(submenu => {
        submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
    });
}

// ╔══════════════════════════════════════════╗
// ║                 [2] EVENTOS              ║
// ╚══════════════════════════════════════════╝
document.addEventListener('DOMContentLoaded', () => {
    const navButtons = document.querySelectorAll('.botao-navegacao');

    navButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                toggleSubmenu();
            }
        });
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.botao-navegacao-wrapper')) {
            document.querySelectorAll('.submenu').forEach(submenu => {
                submenu.style.display = 'none';
            });
        }
    });

    // Adicionando evento de mudança para a classe do defensivo
    const classeSelect = document.getElementById('classe');
    const produtoSelect = document.getElementById('produto');

    if (classeSelect && produtoSelect) {
        classeSelect.addEventListener('change', async () => {
            const classe = classeSelect.value;
            const produtos = await carregarDados(`produtos/${classe}`);
            produtoSelect.innerHTML = '<option value="">Selecione um produto</option>';
            produtos.forEach(produto => {
                const option = document.createElement('option');
                option.value = produto[1]; // Nome do produto
                option.textContent = produto[1]; // Nome do produto
                produtoSelect.appendChild(option);
            });
        });
    }

    // Adicionando evento de mudança para o setor
    const setorSelect = document.getElementById('setor');
    const canteiroSelect = document.getElementById('canteiro');

    if (setorSelect && canteiroSelect) {
        setorSelect.addEventListener('change', async () => {
            const setorId = setorSelect.value;
            const canteiros = await carregarDados(`canteiros/${setorId}`);
            canteiroSelect.innerHTML = '<option value="">Selecione um canteiro</option>';
            canteiros.forEach(canteiro => {
                const option = document.createElement('option');
                option.value = canteiro[0]; // ID do canteiro
                option.textContent = canteiro[1]; // Nome do canteiro
                canteiroSelect.appendChild(option);
            });
        });
    }

    // Adicionando evento de clique ao botão "Registrar" (exemplo)
    const registrarBtn = document.querySelector('button[type="submit"]');
    if (registrarBtn) {
        registrarBtn.addEventListener('click', function() {
            console.log('Botão Registrar clicado!');
            // Adicione aqui o código JavaScript para executar quando o botão for clicado
        });
    }
});

// ╔══════════════════════════════════════════╗
// ║                  [3] API                 ║
// ╚══════════════════════════════════════════╝
async function carregarDados(apiEndpoint) {
    try {
        const response = await fetch(`/api/${apiEndpoint}`);
        return await response.json();
    } catch (erro) {
        console.error(`Erro ao carregar ${apiEndpoint}:`, erro);
        return [];
    }
}
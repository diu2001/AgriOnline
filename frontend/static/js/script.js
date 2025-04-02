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
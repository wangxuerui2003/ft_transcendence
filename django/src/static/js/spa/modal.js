import { MODAL_CONTAINER } from './components/component.js';
import { SignIn } from './components/modals/signin.js';

export const MODALS = {
	signin: new SignIn({ url: '/signin' }),
};

// open modal buttons handler
document.body.addEventListener('click', (e) => {
	if (e.target.matches('[data-modal]')) {
		e.preventDefault();
		const modalName = e.target.getAttribute('data-modal');
		openModal(modalName);
	}
});

export async function openModal(modalName) {
	const modal = MODALS[modalName];
	if (modal) {
		const element = await modal.render();
		MODAL_CONTAINER.innerHTML = '';
		MODAL_CONTAINER.appendChild(element);
		activateModal();
	} else {
		console.error('Modal not found:', modalName);
	}
}

function activateModal() {
	const modalOverlay = document.getElementById('modalOverlay');
	const modal = document.getElementById('modal');
	modalOverlay.classList.add('modal-active');
	modal.classList.add('modal-active');

	function closeModal() {
		modalOverlay.classList.remove('modal-active');
		modal.classList.remove('modal-active');
	}

	document
		.getElementById('closeModalBtn')
		.addEventListener('click', closeModal);

	document.getElementById('modalOverlay').addEventListener('click', closeModal);
}

import { Component } from '../component.js';

export class ForgetPassword extends Component {
	constructor(params) {
		super(params);
	}

	cleanupComponent() {
		super.cleanupComponent();
	}

	template() {
		return `
			<div>
				<h1>Modal</h1>
			</div>
		`;
	}
}

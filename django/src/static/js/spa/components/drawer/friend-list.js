import { Component } from '../component.js';

export class FriendList extends Component {
	constructor(params) {
		super(params);
	}

	template() {
		return `
			<div>
				<h1>Drawer</h1>
			</div>
		`;
	}
}

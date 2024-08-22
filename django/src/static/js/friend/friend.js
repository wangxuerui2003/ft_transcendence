import { FriendList } from '../spa/components/others/friend-list.js';

export async function renderFriendList() {
	const friends = [
		{
			avatar: 'https://via.placeholder.com/150',
			username: 'john_doe',
			nickname: 'John',
		},
		{
			avatar: 'https://via.placeholder.com/150',
			username: 'janedoe',
			nickname: 'Jane',
		},
		{
			avatar: 'https://via.placeholder.com/150',
			username: 'aliceee',
			nickname: 'Alice',
		},
	];

	const friendList = new FriendList({ props: { friends } });
	const friendListElem = document.getElementById('friend-list');
	friendListElem.innerHTML = '';
	friendListElem.appendChild(await friendList.render());
}

renderFriendList();
document.addEventListener('drawer-opened', renderFriendList);

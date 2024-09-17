const getState = ({ getStore, getActions, setStore }) => {
	return {
		store: {
		auth: false, 
		user: {}
		},
		actions: {
			// Use getActions to call a function within a fuction


			login: async (mail, password) => {
				try {
					// fetching data from the backend
					const resp = await fetch(process.env.BACKEND_URL + "login", {
						method: "POST",
						headers: { "Content-Type": "application/json" },
						body: JSON.stringify({
							email: mail,
							password: password
						})
					})
					const data = await resp.json()
					if (resp.status == 200) {
						console.log(data)
						localStorage.setItem("token", data.access_token)
						setStore({auth:true, user: data.user})
						console.log(data.user)
						// don't forget to return something, that is how the async resolves
						return true;
					} else {
						setStore({auth:false})
						return false
					}
				} catch (error) {
					console.log("Error loading message from backend", error)
					return false
				}
			},

			registro: async (mail, password) => {
				try {
					// fetching data from the backend
					const resp = await fetch(process.env.BACKEND_URL + "signup", {
						method: "POST",
						headers: { "Content-Type": "application/json" },
						body: JSON.stringify({
							email: mail,
							password: password
						})
					})
					const data = await resp.json()
					if (resp.status == 201) {
						console.log(data)
						// don't forget to return something, that is how the async resolves
						return true;
					} else {
						return false
					}
				} catch (error) {
					console.log("Error loading message from backend", error)
					return false
				}
			},

		}
	};
};

export default getState;

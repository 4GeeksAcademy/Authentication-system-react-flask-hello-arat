import React, { useContext } from "react";
import { Context } from "../store/appContext";
import { Link } from "react-router-dom";

export const Navbar = () => {
	const { actions, store } = useContext(Context)
	console.log(store.auth)
	return (
		<nav className="navbar navbar-light bg-light">
			<div className="container">
				<Link to="/">
					<span className="navbar-brand mb-0 h1">React Boilerplate</span>
				</Link>
				<div className="ml-auto">
					{!store.auth ?
						<div>


							<Link to="/Login">
								<button className="btn btn-outline-primary mx-2">Login</button>
							</Link>
							<Link to="/Registro">
								<button className="btn btn-outline-primary mx-2">Registrarse</button>
							</Link>
						</div>
						:
						<div>
							<Link to="/">
								<button className="btn btn-outline-primary mx-2" onClick={actions.logOut}>Cerrar Sesion</button>
							</Link>

						</div>
					}
				</div>
			</div>
		</nav>
	);
};

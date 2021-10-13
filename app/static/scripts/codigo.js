function login() {
  user = document.getElementById("user").value;
  pass = document.getElementById("pass").value;

  mensaje = user + " " + pass + " not registered!";

  if (user == "pedro" | user == "cesar"){
    if (pass == "a") {
      mensaje = "Bienvenido " + user;
    }
  }

}

function register() {
  username = document.getElementById("new_user").value;
  pass_1 = document.getElementById("new_pass").value;
  pass_2 = document.getElementById("new_pass_repeat").value;
  email = document.getElementById("new_email").value;
  credit_card = document.getElementById("new_credit_card").value;



  if (pass_1 != pass_2) {
    alert("Las contraseñas introducidas no son iguales!");
    return;
  }

  /* Comprobar si el usuario ya esta registrado */

  mensaje = " El usuario \"" + username + "\" con email \""
  + email + "\" y tajeta de crédito \"" + credit_card +
  "\" ha sido registrado correctamente en el sistema!"

}

function search() {
  film = document.getElementById("film_to_search").value;

  /* Comprobar si la pelicula esta en la base de datos */

  mensaje = "La película " + film + " no está disponible por el momento"

  alert(mensaje);
}

function rent() {
  mensaje = "Alquiler no disponible por el momento"

  alert(mensaje);
}

function auto_submit() {
  document.getElementById("film_action").submit(); 
}

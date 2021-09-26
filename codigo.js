function login() {
  user = document.getElementById("user").value;
  pass = document.getElementById("pass").value;

  mensaje = user + " " + pass + " not registered!";

  if (user == "pedro" | user == "cesar"){
    if (pass == "a") {
      mensaje = "Bienvenido " + user;
    }
  } 

  alert(mensaje);
}

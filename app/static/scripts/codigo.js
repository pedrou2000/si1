
$(document).ready(function(){

    /* Historial de compras */
    $(".hidden_info").hide()
    $(".less_info").hide()
    $(".more_info").on( "click", function() {
        $('#hidden_info_'+this.id).show();
        $('#' + this.id + '.less_info').show();
        $('#' + this.id + '.more_info').hide();
     });
     $(".less_info").on( "click", function() {
        $('#hidden_info_'+this.id).hide();
        $('#' + this.id + '.more_info').show();
        $('#' + this.id + '.less_info').hide();
    });


    /* Comprobacion fortaleza contraseña en register */
    $("#new_pass").keyup(function(){
        let otros_caracteres = /^.*[^a-zA-Z0-9].*$/
        let numeros = /^.*[0-9].*$/
        let letras = /^.*[a-zA-Z].*$/
        let longitud = /^.{0,7}$/

        pass = document.getElementById("new_pass").value;

        if(longitud.test(pass)){
            $('#passtrength').html('Contraseña demasiado corta.');
        } else if (otros_caracteres.test(pass) && letras.test(pass) && numeros.test(pass)) {
            $('#passtrength').html('Fortaleza contraseña: fuerte');
        } else if (letras.test(pass) && (numeros.test(pass) || otros_caracteres.test(pass))) {
            $('#passtrength').html('Fortaleza contraseña: media');
        } else if (letras.test(pass) || numeros.test(pass) || otros_caracteres.test(pass)) {
            $('#passtrength').html('Fortaleza contraseña: débil');
        }

    });


});

window.onload = function(){
    if(document.cookie) {
        var username = document.cookie.split("=")[1];
        document.getElementById('user').value = username;
    }
    //alert('window')
}

function login() {
    user = document.getElementById("user").value;
    pass = document.getElementById("pass").value;

    if (user == "") {
        alert("Enter a username.")
        return;
    }

    document.cookie = "username="+user

    document.getElementById("login_form").submit()
}

function register() {
    username = document.getElementById("new_user").value;
    pass_1 = document.getElementById("new_pass").value;
    pass_2 = document.getElementById("new_pass_repeat").value;
    email = document.getElementById("new_email").value;
    credit_card = document.getElementById("new_credit_card").value;
    direccion_envio = document.getElementById("direccion_envio").value;

    // comprobaciones username
    let letras_o_numeros = /^[a-zA-Z0-9]+$/;
    if(!letras_o_numeros.test(username)){
        alert("El usuario debe ser una cadena de numeros y letras.");
        return;
    }
    if(username.length < 6){
        alert("El usuario debe tener al menos 6 caracteres.");
        return;
    }

    // comprobaciones correo
    let correo = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/
    if(!correo.test(email)){
        alert("Introduzca un email valido.");
        return;
    }

    // comprobaciones contraseña
    if (pass_1.length < 8) {
        alert("La contraseña debe tener al menos 8 caracteres.");
        return;
    }
    if (pass_1 != pass_2) {
        alert("Las contraseñas introducidas no son iguales.");
        return;
    }

    // comprobaciones tarjeta credito
    let numeros = /^[0-9]+$/
    if (credit_card.length != 16 || !numeros.test(credit_card)) {
        alert("El numero de tarjeta debe contener 16 digitos.");
        return;
    }

    // comprobaciones direccion envio
    if (direccion_envio.length > 50) {
        alert("La direccion de envio es demasiado larga.");
        return;
    }

    document.getElementById("register_form").submit()
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

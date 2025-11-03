const tiempoEstudioBase = TIEMPO_ESTUDIO_BASE; 
const tiempoDescansoBase = TIEMPO_DESCANSO_BASE;

let tiempoEstudioInicial = tiempoEstudioBase; 
let tiempoDescansoInicial = tiempoDescansoBase;

let estaCorriendo = false;
let esModoEstudio = true;
let tiempoRestante = tiempoEstudioInicial;
let intervaloTemporizador;

const visorTiempo = document.getElementById('tiempo-visor');
const visorModo = document.getElementById('modo-actual');
const btnIniciar = document.getElementById('btn-iniciar');
const btnPausar = document.getElementById('btn-pausar');
const btnReiniciar = document.getElementById('btn-reiniciar');
const inputEstudio = document.getElementById('input-estudio');
const inputDescanso = document.getElementById('input-descanso');
const btnAceptar = document.getElementById('btn-aceptar');
        
function actualizarVista() {
    const horas = Math.floor(tiempoRestante / 3600);
    const segundosDespuesDeHoras = tiempoRestante % 3600;
    const minutos = Math.floor(segundosDespuesDeHoras / 60);
    
    const segundos = segundosDespuesDeHoras % 60;
    
    const horasVisor = String(horas).padStart(2, '0');
    const minutosVisor = String(minutos).padStart(2, '0');
    const segundosVisor = String(segundos).padStart(2, '0');
    
    const visor = `${horasVisor}:${minutosVisor}:${segundosVisor}`;
        
    visorTiempo.textContent = visor;
}

function cambiarModo() {
    esModoEstudio = !esModoEstudio;
    btnIniciar.disabled = false;
    
    if (esModoEstudio) {
        tiempoRestante = tiempoEstudioInicial;
        visorModo.innerHTML = "Modo <span class='text-main-violet'>Estudio</span>";
    } else {
        tiempoRestante = tiempoDescansoInicial;
        visorModo.innerHTML = "Modo <span class='text-green'>Descanso</span>";
    }
    actualizarVista();
}
        
function tic() {
    if (tiempoRestante > 0) {
        tiempoRestante--;
        actualizarVista();
    } else {
        // Detiene el temporizador
        clearInterval(intervaloTemporizador);
        estaCorriendo = false; 

        let title, text; // varibles para la libreria de alertas
        const textoDeModo = esModoEstudio ? 'descanso' : 'estudio'; 

        if (esModoEstudio) {
            title = "¡Éxito!";
            text = "¡Tiempo de <span class='text-main-violet'>estudio</span> terminado! Hora de descansar.";
        } else {
            title = "¡Bien!";
            text = "¡<span class='text-green'>Descanso</span> terminado! De vuelta al trabajo.";
        }

        alertify.alert(title, text, function(){
            cambiarModo();
            iniciarTemporizador()
            }).set({
                'label': 'Comenzar ' + textoDeModo
        }); 
    }
}

function aceptarTiempos() {
    const nuevoTiempoEstudioMin = parseInt(inputEstudio.value);
    const nuevoTiempoDescansoMin = parseInt(inputDescanso.value);
    
    tiempoEstudioInicial = nuevoTiempoEstudioMin * 60;
    tiempoDescansoInicial = nuevoTiempoDescansoMin * 60;
    
    reiniciarTemporizador();
    iniciarTemporizador();
    alertify.success(`Tiempos actualizados: Estudio ${nuevoTiempoEstudioMin} min | Descanso ${nuevoTiempoDescansoMin} min`);
}

function iniciarTemporizador() {
    if (!estaCorriendo) {
        estaCorriendo = true;
        btnIniciar.disabled = true;
        btnPausar.disabled = false;
        intervaloTemporizador = setInterval(tic, 1000); 
    }
}

function pausarTemporizador() {
    if (estaCorriendo) {
        estaCorriendo = false;
        btnIniciar.disabled = false;
        btnPausar.disabled = true;
        clearInterval(intervaloTemporizador);
    }
}

function reiniciarTemporizador() {
    pausarTemporizador();
    esModoEstudio = true;
    tiempoRestante = tiempoEstudioInicial;
    visorModo.innerHTML = "Modo <span class='text-main-violet'>Estudio</span>";
    actualizarVista();
}

btnIniciar.addEventListener('click', iniciarTemporizador);
btnPausar.addEventListener('click', pausarTemporizador);
btnReiniciar.addEventListener('click', reiniciarTemporizador);
btnAceptar.addEventListener('click', aceptarTiempos);

inputEstudio.value = tiempoEstudioInicial / 60; 
inputDescanso.value = tiempoDescansoInicial / 60;

actualizarVista();
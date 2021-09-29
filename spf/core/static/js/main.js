function createMessage(msg){
    divAlert = document.createElement('div');
    divAlert.classList.add('alert', 'alert-danger', 'alert-dismissible', 'fade', 'show', 'is-no-rounded', 'm-0', 'p-2');
    divAlert.setAttribute('role', 'alert');

    divContainer = document.createElement('div');
    divContainer.classList.add('container', 'text-center');
    divContainer.innerHTML = msg;

    btnClose = document.createElement('button');
    btnClose.type = 'button';
    btnClose.classList.add('btn-close', 'btn-sm', 'm-1', 'p-2');
    btnClose.setAttribute('data-bs-dismiss', 'alert');
    btnClose.setAttribute('aria-label', 'Close');

    divContainer.appendChild(btnClose);
    divAlert.appendChild(divContainer);

    return divAlert;
}


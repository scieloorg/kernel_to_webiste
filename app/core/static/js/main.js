function createMessage(msg, alert_class){
    /* 
    Cria mensagem de alerta na interface gráfica.

    Parameters
    ----------
    msg: string
    alert_class: classe CSS, por exemplo: alert alert-is-danger
    */
    divAlert = document.createElement('div');
    divAlert.classList.add('alert', alert_class, 'alert-dismissible', 'fade', 'show', 'is-no-rounded', 'm-0', 'p-2');
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

function ingressPackageSearchPopulateTable(data){
    /*
    Preenche tabela resultante de busca por pacote.

    Parameters
    ----------
    data: array
    */
    packagesTable = document.getElementById('packagesTable');
    tableBody = document.getElementById('packagesTableBody');
    packagesTable.style.display = 'block';

    row = tableBody.insertRow(-1);

    pkg_version = row.insertCell(-1);
    pkg_version.innerHTML = data['name'];

    pkg_version = row.insertCell(-1);
    pkg_version.innerHTML = data['version'];

    pkg_created = row.insertCell(-1)
    pkg_created.innerHTML = formatDate(new Date(data['created']));

    addLinkCellToRow(row, 'ZIP', data['uri'])

    var divBaseMessages = document.getElementById('baseMessages');
    cleanMessages(divBaseMessages);
    element_message = createMessage(gettext('Package was generated with success.'), 'alert-success');
    divBaseMessages.append(element_message);
}

    }
}

function showLoader(loader, button){
    /*
    Exibe um gif do tipo loading para indicar que dados estão sendo obtidos.

    Parameters
    ----------
    loader: Elemento `<div>`
    button: Elemento `<button>`
    */
    loader.style.display = 'block';
    button.setAttribute('disabled', 'disabled');
}

function hideLoader(loader, button){
    /*
    Oculta um gif do tipo loading para indicar que dados estão sendo obtidos.

    Parameters
    ----------
    loader: Elemento `<div>`
    button: Elemento `<button>`
    */
    loader.style.display = 'none';
    button.removeAttribute('disabled');
}

function setEventStatusCompleted(object){
    /*
    Sobrescreve estado de evento.

    Parameters
    ----------
    object: Elemento `<td>`
    */
    object.innerHTML = gettext('Completed');
    object.classList.remove('bg-warning');
    object.classList.add('bg-success');
}

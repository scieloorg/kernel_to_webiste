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

function ingressPackageUploadPopulateTable(data, journal_uri){
    /*
    Preenche tabela resultante de envio de pacote.

    Parameters
    ----------
    data: array
    journal_uri: string
    */
    div_uploaded_packages = document.getElementById('div_uploaded_packages');
    div_uploaded_packages.style.display = "initial";

    tbody_uploaded_packages = document.getElementById('tbody_uploaded_packages');

    for (var i = 0; i < data['article_files'].length; i++){
        row = tbody_uploaded_packages.insertRow(-1);

        cell_package_file = row.insertCell(-1);
        cell_package_file.innerHTML = data['package_file'];

        cell_issn = row.insertCell(-1);
        cell_issn.innerHTML = data['article_files'][i]['issn']

        var acronym_text = data['article_files'][i]['acron'];
        var journal_link = journal_uri + acronym_text;
        addLinkCellToRow(row, acronym_text, journal_link);

        var pid_text = data['article_files'][i]['pid'];
        var pid_link = journal_uri + acronym_text + '/a/' + pid_text;
        addLinkCellToRow(row, pid_text, pid_link);

        var file_text = data['article_files'][i]['file']['name'];
        var file_link = data['article_files'][i]['file']['uri'];;
        addLinkCellToRow(row, file_text, file_link);

        cell_version = row.insertCell(-1)
        cell_version.innerHTML = data['article_files'][i]['version'];

        cell_datetime = row.insertCell(-1)
        cell_datetime.innerHTML = formatDate(new Date(data['datetime']));
    }
}

function addLinkCellToRow(row, text, href){
    /*
    Adiciona célula do tipo link a um objeto `<tr>`.

    Parameters
    ----------
    row: `<tr>`
    text: string
    href: string
    */
    link = document.createElement('a')
    link.text = text;
    link.href = href;
    link.classList.add('link');
    link.setAttribute('target', '_blank');
    cell = row.insertCell(-1);
    cell.appendChild(link);
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

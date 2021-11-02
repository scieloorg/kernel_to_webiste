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

function ingressPackageDownloadToggleSpinner(){
    var btnSearchPackage = document.getElementById('btnSearchPackage');
    var divSpinner = document.getElementById('searchPackageLoading');
    if (divSpinner.style.display == "none") {
        divSpinner.style.display = 'block';
        btnSearchPackage.setAttribute('disabled', 'disabled');
    } else {
        divSpinner.style.display = 'none';
        btnSearchPackage.removeAttribute('disabled');
    }
}

function ingressPackageDownloadCreateTable(data){
    tableBody = document.getElementById('resultSearchPackagesTableBody')

    for (k in data['doc_pkgs']){
        els = data['doc_pkgs'][k];
        row = tableBody.insertRow(-1);

        aResult = document.createElement('a')
        aResult.text = els['name'];
        aResult.href = els['uri'];
        aResult.classList.add('link');

        tdUri = row.insertCell(-1);
        tdUri.appendChild(aResult);

        tdCreated = row.insertCell(-1);
        tdCreated.innerHTML = els['created'];

        tdUpdated = row.insertCell(-1);
        tdUpdated.innerHTML = els['updated'];
    }

    if (data['doc_pkgs'].length > 0) {
        document.getElementById('resultSearchPackages').style.display = 'block';
    } else {
        var divBaseMessages = document.getElementById('baseMessages');
        for (k in data['errors']){
            element_message = createMessage(data['errors'][k]);
            divBaseMessages.append(element_message);
        }
    }
}

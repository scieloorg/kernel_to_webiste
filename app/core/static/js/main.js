function createMessage(msg, alert_class){
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

function ingressPackageDownloadCreateTable(data){
    tableBody = document.getElementById('resultSearchPackagesTableBody')

    counter = 1
    for (k in data['doc_pkgs']){
        els = data['doc_pkgs'][k];
        row = tableBody.insertRow(-1);

        tdUri = row.insertCell(-1);
        tdUri.innerHTML = counter;

        aPkgName = document.createElement('a')
        aPkgName.text = els['name'];
        aPkgName.href = els['uri'];
        aPkgName.classList.add('link');

        tdPkgName = row.insertCell(-1);
        tdPkgName.appendChild(aPkgName);

        tdCreated = row.insertCell(-1)
        tdCreated.innerHTML = new Date(els['created']);

        counter += 1;
    }

    if (data['doc_pkgs'].length > 0) {
        document.getElementById('resultSearchPackages').style.display = 'block';
    } else {
        var divBaseMessages = document.getElementById('baseMessages');
        for (k in data['errors']){
            element_message = createMessage(data['errors'][k], 'alert-danger');
            divBaseMessages.append(element_message);
        }
    }
}

function showLoader(loader, button){
    loader.style.display = 'block';
    button.setAttribute('disabled', 'disabled');
}

function hideLoader(loader, button){
    loader.style.display = 'none';
    button.removeAttribute('disabled');
}

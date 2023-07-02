var save_action = document.getElementById('save-action');

document.addEventListener("DOMContentLoaded", function () {
    modal_containers = document.getElementById('modal-containers');

    modals = document.querySelectorAll('.modal');
    modals.forEach(function (modal) {
        modal_containers.prepend(modal);
    })
});

function hideModal(modal_str) {
    modals = document.querySelectorAll(modal_str);
    //console.log(modals);
    modals.forEach(function (modal) {
        if (modal.parentElement.className !== "") {
            modal.remove()
        } else {
            console.log(modal_str)
            bootstrap.Modal.getOrCreateInstance((modal)).hide();
        }
        //console.log(modal.parentNode.nodeName)
    });
    console.log('hideModal', modal_str);
}


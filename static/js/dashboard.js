function downloadSelected() {
    const checkboxes= document.querySelectorAll('.select-file:checked');
    checkboxes.forEach(cb => {
        const link = cb.getAttribute('data-link');
        const a = document.createElement('a');
        a.href = link;
        a.download = '';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });
}

function downloadFile(url, filename) {
    const progressBar = document.getElementById("downloadProgress");
    const progressText = document.getElementById("progressText");
    
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.responseType = "blob";
    
    xhr.onprogress = function (event) {
        if (event.lengthComputable) {
            let percent = Math.round((event.loaded / event.total) * 100);
            progressBar.value = percent;
            progressText.innerText = percent + "%";
        }
    };
    
    xhr.onload = function () {
        const blob = xhr.response;
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
        link.click();
        
        progressBar.value = 0;
        progressText.innerText = "Done";
    };
    
    xhr.send();
}
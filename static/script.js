const fileInput = document.getElementById("fileInput");
const uploadArea = document.getElementById("uploadArea");

const previewSection = document.getElementById("previewSection");
const previewImage = document.getElementById("previewImage");

const removeBtn = document.getElementById("removeBtn");
const detectBtn = document.getElementById("detectBtn");

const resultSection = document.getElementById("resultSection");
const resultImage = document.getElementById("resultImage");

const objectList = document.getElementById("objectList");
const totalObjects = document.getElementById("totalObjects");

let selectedFile = null;


// ==========================================
// SELECT IMAGE
// ==========================================

fileInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) {
        return;
    }

    handleFile(file);
});


// ==========================================
// HANDLE IMAGE
// ==========================================

function handleFile(file) {

    if (!file.type.startsWith("image/")) {

        alert("Please select an image file.");

        return;
    }

    selectedFile = file;

    const reader = new FileReader();

    reader.onload = function (event) {

        previewImage.src = event.target.result;

        uploadArea.classList.add("hidden");

        previewSection.classList.remove("hidden");

        resultSection.classList.add("hidden");

    };

    reader.readAsDataURL(file);
}


// ==========================================
// REMOVE IMAGE
// ==========================================

removeBtn.addEventListener("click", function () {

    selectedFile = null;

    fileInput.value = "";

    previewImage.src = "";

    resultImage.src = "";

    previewSection.classList.add("hidden");

    uploadArea.classList.remove("hidden");

    resultSection.classList.add("hidden");

    objectList.innerHTML = "";

    totalObjects.textContent = "0";

});


// ==========================================
// DETECT OBJECTS
// ==========================================

detectBtn.addEventListener("click", async function () {

    if (!selectedFile) {

        alert("Please select an image first.");

        return;
    }


    const formData = new FormData();

    formData.append("file", selectedFile);


    detectBtn.disabled = true;

    detectBtn.innerHTML = `
        <span>Detecting Objects...</span>
        <span>⏳</span>
    `;


    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });


        if (!response.ok) {

            throw new Error(
                "Server error: " + response.status
            );
        }


        const data = await response.json();

        console.log("Detection result:", data);


        if (!data.success) {

            throw new Error(
                data.error || "Detection failed."
            );
        }


        // --------------------------------------
        // SHOW DETECTED IMAGE
        // --------------------------------------

        resultImage.src =
            data.result_url +
            "?t=" +
            new Date().getTime();


        // --------------------------------------
        // SHOW OBJECTS
        // --------------------------------------

        objectList.innerHTML = "";


        if (
            data.objects &&
            data.objects.length > 0
        ) {

            data.objects.forEach(function (object) {

                addObject(
                    object.name,
                    object.count
                );

            });

        } else {

            addObject(
                "No objects detected",
                "0"
            );
        }


        // --------------------------------------
        // TOTAL
        // --------------------------------------

        totalObjects.textContent =
            data.total;


        // --------------------------------------
        // SHOW RESULT SECTION
        // --------------------------------------

        resultSection.classList.remove("hidden");


        setTimeout(function () {

            resultSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 200);


    } catch (error) {

        console.error(error);

        alert(
            "Detection failed: " +
            error.message
        );

    } finally {

        detectBtn.disabled = false;

        detectBtn.innerHTML = `
            <span>Detect Objects</span>
            <span>→</span>
        `;
    }

});


// ==========================================
// ADD OBJECT
// ==========================================

function addObject(name, count) {

    const item =
        document.createElement("div");

    item.className = "object-item";


    const nameElement =
        document.createElement("span");

    nameElement.className =
        "object-name";

    nameElement.textContent =
        name;


    const countElement =
        document.createElement("span");

    countElement.className =
        "object-count";

    countElement.textContent =
        count;


    item.appendChild(nameElement);

    item.appendChild(countElement);

    objectList.appendChild(item);
}


// ==========================================
// DRAG & DROP
// ==========================================

uploadArea.addEventListener(
    "dragover",
    function (event) {

        event.preventDefault();

        uploadArea.style.borderColor =
            "#4f46e5";

    }
);


uploadArea.addEventListener(
    "dragleave",
    function () {

        uploadArea.style.borderColor = "";

    }
);


uploadArea.addEventListener(
    "drop",
    function (event) {

        event.preventDefault();

        uploadArea.style.borderColor = "";

        const file =
            event.dataTransfer.files[0];

        if (file) {

            handleFile(file);

        }

    }
);
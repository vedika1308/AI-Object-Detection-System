let countTimer;

function startDetection() {

    const video = document.getElementById("video");

    video.src = "/video_feed";
    video.style.display = "block";

    countTimer = setInterval(updateCounts, 500);
}

function stopDetection() {

    const video = document.getElementById("video");

    video.src = "";
    video.style.display = "none";

    clearInterval(countTimer);

    document.getElementById("total").innerText = "0";
    document.getElementById("person").innerText = "0";
    document.getElementById("car").innerText = "0";
    document.getElementById("bottle").innerText = "0";
}

function updateCounts() {

    fetch("/counts")
        .then(response => response.json())
        .then(data => {

            let total = 0;

            for (let object in data) {
                total += data[object];
            }

            document.getElementById("total").innerText = total;

            document.getElementById("person").innerText =
                data.person || 0;

            document.getElementById("car").innerText =
                data.car || 0;

            document.getElementById("bottle").innerText =
                data.bottle || 0;
        });
}
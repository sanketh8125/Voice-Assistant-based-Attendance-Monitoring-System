document.getElementById("ask-start-mic").addEventListener("click", function () {
    document.getElementById("ask-start-mic").disabled = true;
    document.getElementById("start-mic").disabled = true;
    let statusElement = document.getElementById("ask-status");

    // Check if browser supports SpeechRecognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        statusElement.textContent = "Your browser does not support Speech Recognition.";
        return;
    }

    let recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.start();

    recognition.onstart = function () {
        statusElement.textContent = "Listening...";
        console.log("lis");
    };

    recognition.onspeechend = function () {
        recognition.stop();
        // statusElement.textContent = "Processing...";
        console.log("end");
    };


    recognition.onresult = function (event) {
        try {
            let spokenText = event.results[0][0].transcript.trim();
            console.log("You said:", spokenText);
            Askquery(spokenText, statusElement);
            // setTimeout(function () {
            //     location.reload();
            // }, 2000);
        } catch (error) {
            console.error("Error in processing result:", error);
            statusElement.textContent = "Error processing speech result.";
        }
    };

    recognition.onerror = function (event) {
        statusElement.textContent = "Error: " + event.error;
        if (event.error == "no-speech") {
            statusElement.textContent = "Error I didn't hear";
            speakText("Sorry, I didn't hear you, try again")
            // speakText("Your attendance overview shows that you were present for  5 out of  10 days, resulting in a  50% attendance rate.")
        }
        // setTimeout(function () {
        //     location.reload();
        // }, 4500);
    };

    function Askquery(spokenText, statusElement) {
        fetch("/home/responding/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ spoken_response: spokenText })
        })
            .then(response => {
                console.log("Fetch request sent!", response);  // Debugging
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    statusElement.textContent = `✅ ${data.message}`;
                    speakText(data.message);
                    // setTimeout(() => location.reload(), 10000);

                } else {
                    statusElement.textContent = `❌ ${data.message}`;
                    speakText(data.message);
                }
            })
            .catch(error => {
                console.error(error);
                statusElement.textContent = "Error marking attendance.";
                speakText("Error marking attendance");
            });
            // setTimeout(function () {
            //     location.reload();
            // }, 2000);
    }
});
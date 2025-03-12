document.addEventListener('DOMContentLoaded', function() {

    var carousel = document.getElementById('carouselExampleCaptions');
    
    carousel.addEventListener('slid.bs.carousel', function (event) {
        var activeSlide = document.querySelector('#carouselExampleCaptions .carousel-item.active');
        var activeIndex = Array.from(carousel.querySelectorAll('.carousel-item')).indexOf(activeSlide);
        
        var one = document.getElementById("divOne");
        var two = document.getElementById("divTwo");
        var three = document.getElementById("divThree");

        // Hide all divs first
        one.style.display = "none";
        two.style.display = "none";
        three.style.display = "none";

        // Show the correct div based on the slide index
        if(activeIndex === 0){
            one.style.display = "block";
        } 
        else if(activeIndex === 1){
            two.style.display = "block";
        } 
        else if(activeIndex === 2){
            three.style.display = "block";
        }
    });

    // Run once on page load to sync the content with the default active slide
    changeContentBasedOnActiveSlide();
});

function changeContentBasedOnActiveSlide(){
    var carousel = document.getElementById('carouselExampleCaptions');
    var activeSlide = document.querySelector('#carouselExampleCaptions .carousel-item.active');
    var activeIndex = Array.from(carousel.querySelectorAll('.carousel-item')).indexOf(activeSlide);
    
    var one = document.getElementById("divOne");
    var two = document.getElementById("divTwo");
    var three = document.getElementById("divThree");

    // Reset all displays
    one.style.display = "none";
    two.style.display = "none";
    three.style.display = "none";

    // Show the correct content
    if(activeIndex === 0){
        one.style.display = "block";
    } 
    else if(activeIndex === 1){
        two.style.display = "block";
    } 
    else if(activeIndex === 2){
        three.style.display = "block";
    }
}




async function checkGrammar(message) {
    const apiUrl = "https://api.languagetool.org/v2/check"; // API endpoint for grammar check
    const data = {
        text: message, 
        language: "en-US"
    };

    try {
        const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams(data),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        let correctedMessage = message; // Keep the original message
        let explanation = ""; // Store corrections

        if (result.matches?.length > 0) { 
            result.matches.forEach(match => { 
                const { replacements, offset, length } = match;
                if (replacements?.length > 0) { 
                    correctedMessage = correctedMessage.substring(0, offset) + 
                                       replacements[0].value + 
                                       correctedMessage.substring(offset + length);
                    explanation += `Correction: '${message.substring(offset, offset + length)}' → '${replacements[0].value}'. `;
                }
            });
        }

        return { correctedMessage, explanation }; // Return the corrected message and explanation
    } catch (error) {
        console.error("Error checking grammar:", error);
        return { correctedMessage: message, explanation: "Grammar check failed." };
    }
}

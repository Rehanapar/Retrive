var element = $('.floating-chat');
var myStorage = localStorage;

const captchaForm = document.querySelector('.captcha-form');
let chatResponse = document.createElement('li');

// console.log(captchaForm);
if (!myStorage.getItem('chatID')) {
    myStorage.setItem('chatID', createUUID());
}

setTimeout(function () {
    element.addClass('enter');
}, 1000);

element.click(openElement);

function openElement() {
    var messages = element.find('.messages');
    var textInput = element.find('.text-box');
    element.find('>i').hide();
    element.addClass('expand');
    element.find('.chat').addClass('enter');
    var strLength = textInput.val().length * 2;
    textInput.keydown(onMetaAndEnter).prop("disabled", false).focus();
    element.off('click', openElement);
    element.find('.header button').click(closeElement);
    element.find('#sendMessage').click(sendNewMessage);
    messages.scrollTop(messages.prop("scrollHeight"));
}

function closeElement() {
    element.find('.chat').removeClass('enter').hide();
    element.find('>i').show();
    element.removeClass('expand');
    element.find('.header button').off('click', closeElement);
    element.find('#sendMessage').off('click', sendNewMessage);
    element.find('.text-box').off('keydown', onMetaAndEnter).prop("disabled", true).blur();
    setTimeout(function () {
        element.find('.chat').removeClass('enter').show()
        element.click(openElement);
    }, 500);
}

function createUUID() {
    // http://www.ietf.org/rfc/rfc4122.txt
    var s = [];
    var hexDigits = "0123456789abcdef";
    for (var i = 0; i < 36; i++) {
        s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
    }
    s[14] = "4"; // bits 12-15 of the time_hi_and_version field to 0010
    s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1); // bits 6-7 of the clock_seq_hi_and_reserved to 01
    s[8] = s[13] = s[18] = s[23] = "-";

    var uuid = s.join("");
    return uuid;
}

function sendNewMessage() {
    var userInput = $('.text-box');
    var newMessage = userInput.html().replace(/\<div\>|\<br.*?\>/ig, '\n').replace(/\<\/div\>/g, '').trim().replace(/\n/g, '<br>');

    if (!newMessage) return;

    var messagesContainer = $('.messages');

    messagesContainer.append([
        '<li class="other">',
        newMessage,
        '</li>'
    ].join(''));

    let loadingChat = document.createElement('li')
    loadingChat.classList.add('self')
    loadingChat.classList.add('loading-chat')
    loadingChat.innerText = ""
    messagesContainer.append(loadingChat)

    let loadingDotsContainer = document.createElement('div');
    loadingDotsContainer.classList.add('dots-container');
    loadingChat.appendChild(loadingDotsContainer);

    for (let i = 0; i < 3; i++) {
        let loadingDots = document.createElement('div');
        loadingDots.classList.add('dot');
        loadingDotsContainer.appendChild(loadingDots);
    }

    // clean out old message
    // userInput.html('');
    // focus on input
    userInput.focus();

    messagesContainer.finish().animate({
        scrollTop: messagesContainer.prop("scrollHeight")
    }, 250);
}

function onMetaAndEnter(event) {
    if ((event.metaKey || event.ctrlKey) && event.keyCode == 13) {
        sendNewMessage();
    }
}
document.addEventListener('DOMContentLoaded', function () {
    const floatingChat = document.getElementById('floatingChat');
    const closeChat = document.getElementById('closeChat');

    floatingChat.addEventListener('click', () => {
        floatingChat.classList.remove('blob');
    });

    closeChat.addEventListener('click', () => {
        floatingChat.classList.add('blob');
    });
});


window.onload = (event)=>{
    event.preventDefault();
    // const captchaResponse = grecaptcha.getResponse()
    // document.getElementById('sendMessage').disabled = false;
    document.getElementById("response").contentEditable = true;
    // console.log(params.toString());
    fetch('http://127.0.0.1:5000/chatbot', {
        method: "GET",
    })
        .then(res => res.json())
        .then(

            response => {
                // console.log(response)
                if (response.success) {
                    // console.log(response.message)
                    // return response.message

                    // captchaForm.remove();
                    chatResponse.classList.add("self");
                    chatResponse.innerText = response.message;
                    document.querySelector(".messages").appendChild(chatResponse);
                    // displayResponseWordByWord(response.message)
                }
            }
        )
        .catch(err => console.log(err));
};

function displayResponseWordByWord(responseMessage) {
    const words = responseMessage.split(" ");
    const messagesContainer = document.querySelector(".messages");
    const chatResponse = document.createElement("li");
    chatResponse.classList.add("self");
    // chatResponse.dataset.questionId = questionId;
    messagesContainer.appendChild(chatResponse);
    let wordIndex = 0;
    let likeValue = 0;
    let dislikeValue = 0;
    const interval = setInterval(() => {
        if (wordIndex < words.length) {
            chatResponse.innerHTML += words[wordIndex] + " ";
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: "smooth",
            });
            wordIndex++;
        } else {
            // const feedbackContainer = document.createElement("div");
            // feedbackContainer.classList.add("feedback-container");
            // const likeButton = document.createElement("div");
            // likeButton.classList.add("like-button");
            // likeButton.innerHTML = '<i class="fa fa-thumbs-up"></i>';
            // const dislikeButton = document.createElement("div");
            // dislikeButton.classList.add("dislike-button");
            // dislikeButton.innerHTML = '<i class="fa fa-thumbs-down"></i>';
            // feedbackContainer.appendChild(likeButton);
            // feedbackContainer.appendChild(dislikeButton);
            // chatResponse.appendChild(feedbackContainer);
            // let sessionToken;
            // if (sessionStorage.length > 0) {
            //     sessionToken = sessionStorage.getItem("Token");
            // }
            // likeButton.addEventListener("click", function () {
            //     likeButton.classList.add("clicked");
            //     dislikeButton.classList.remove("clicked");
            //     if (likeValue === 0) {
            //         likeValue = 1;
            //         dislikeValue = 0;
            //         let response = responseMessage;
            //         let likedResponses =
            //             JSON.parse(sessionStorage.getItem("likedResponses")) || [];
            //         likedResponses.push(response);
            //         sessionStorage.setItem(
            //             "likedResponses",
            //             JSON.stringify(likedResponses)
            //         );
            //     } else {
            //         likeValue = 0;
            //         dislikeValue = 0;
            //         likeButton.classList.remove("clicked");
            //     }
            //     // let questionId = chatResponse.dataset.questionId;
            //     let impression = likeValue || dislikeValue * -1;
            //     let sessionToken;
            //     if (sessionStorage.length > 0) {
            //         sessionToken = sessionStorage.getItem("Token");
            //     }
                // sendFeedbackToBackend(impression, questionId, sessionToken);
            // });
            // dislikeButton.addEventListener("click", function () {
            //     dislikeButton.classList.add("clicked");
            //     likeButton.classList.remove("clicked");
            //     if (dislikeValue === 0) {
            //         dislikeValue = -1;
            //         likeValue = 0;
            //         let response = responseMessage;
            //         let dislikedResponses =
            //             JSON.parse(sessionStorage.getItem("dislikedResponses")) || [];
            //         dislikedResponses.push(response);
            //         sessionStorage.setItem(
            //             "dislikedResponses",
            //             JSON.stringify(dislikedResponses)
            //         );
            //     } else {
            //         dislikeValue = 0;
            //         likeValue = 0;
            //         dislikeButton.classList.remove("clicked");
            //     }
                // let questionId = chatResponse.dataset.questionId;
            //     let impression = dislikeValue || likeValue * -1;
            //     let sessionToken;
            //     if (sessionStorage.length > 0) {
            //         sessionToken = sessionStorage.getItem("Token");
            //     }
            //     // sendFeedbackToBackend(impression, questionId, sessionToken);
            // });
            clearInterval(interval);
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: "smooth",
            });
        }
    }, 100);
}

function userResponse(event) {
    event.preventDefault();
    
    const responseInput = document.getElementById('response');
    // console.log(responseInput)
    const question = responseInput.innerText;
    // console.log(question)
    const jsonData = JSON.stringify({ question: question });
    // console.log(jsonData)

    responseInput.innerHTML = '';
    // Send the fetch request with the user's input
    fetch('your api url here', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: jsonData
    })
        .then(res => res.json())
        .then(response => {
            if (!response.success) {
                // console.log(`No response ${response.Errors}`)
                const chatResponse = document.createElement("li");
                chatResponse.classList.add("self");
                chatResponse.innerText = response.message;
                document.querySelector(".messages").appendChild(chatResponse);
                return;
            };
            // console.log(response.message)

            document.querySelector('.loading-chat').remove();
            displayResponseWordByWord(response.message);
            // const chatResponse = document.createElement("li");
            // chatResponse.classList.add("self");
            // chatResponse.innerText = response.message;
            // document.querySelector(".messages").appendChild(chatResponse);

            var messagesContainer = document.querySelector('.messages');
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        })
        .catch(err => console.log(err));
}

function handleKeyPress(event) {
    if (!event.shiftKey && event.keyCode === 13) {
        event.preventDefault();
        sendNewMessage();
        userResponse(event);

        var messagesContainer = document.querySelector('.messages');
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }
}
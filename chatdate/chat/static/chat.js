function do_poll() {
    // short poll to let the back end know this user is still available for chat
    // TODO: maybe tie this into the socketio?
    $.getJSON(short_poll_url, function(json) {
        if(json == "OK") {
            return;
        }

        $("#online_section .users").remove();
        
        $.each(json, function(user) {
            var template = $("#user_template").text();
            var dom = Mustache.render(template, user);
            console.log(dom);
            $("#online_section").append($(dom));
        });
    });
}

do_poll();
setInterval(do_poll, 30000);

var socket = new io.Socket();
socket.connect();
socket.on('connect', function() {
    // through this channel I will send and recieve all chat messages.
    // and maybe possibly other things.
    socket.subscribe(my_hash);
});
socket.on('message', function(data) {
    console.log("got message: ", data);
    add_to_chatbox(data);
});

function add_to_chatbox(data) {
    // Add a message coming back from the server to the chatbox.
    // 'data' is the raw payload from socketio.

    var chat_hash = data.sent_by.hash;
    if(data.sent_by.hash == my_hash) {
        chat_hash = data.sent_to.hash;
    }
    var chat_container = $("#" + chat_hash);
    if(chat_container.length == 0) {
        // this chat messag has come from a new user. Make a new box.
        make_new_chat(data.sent_by.hash, data.sent_by.nickname);
        chat_container = $("#" + chat_hash);
    }

    $.each(data.payload, function(key, value) {
        var li = $("<li>");
        if(key == 'chat') {
            var n = data.sent_by.nickname;
            var line = "<span class='chat-message chat-message-" + n + "'>&lt;" + n + "&gt;</span> " + value;
            li.html(line);
        } else if (key == 'event') {
            li.html("<span class='chat_event'>" + value + "</span>");
        }
        chat_container.find("ul").append(li);
    });

    var chatbox = chat_container.find(".chatbox");
    chatbox.scrollTop(chatbox[0].scrollHeight);
}

function make_new_chat(hash, nickname) {
    // make a new chatbox, and bind the sending events.

    $("#chat_section").show();

    var chat_element = $("#" + channel);
    if(chat_element.length) {
        chat_element.show();
    } else {
        var new_chatbox = $("#chat_template").clone().attr("id", hash);
        new_chatbox.find(".chat_title").text(nickname);
        $("#chat_section").append(new_chatbox);
    }

    new_chatbox.submit(function(event) {
        return send_chat_message(hash, nickname);
    });
}

function send_chat_message(to_hash, to_nickname) {
    // Add a new line to the chat when the "send" button is pressed or
    // enter key is pressed. This function gets binded to new chatboxes when
    // they are created
    var chatbox =  $('#' + to_hash);
    var textbox = chatbox.find("input[type=text]");
    var message = textbox.val();

    if(!message) {
        return false
    }

    socket.send({
        payload: {
            chat: message
        },
        sent_by: {
            nickname: my_nickname,
            hash: my_hash,
        },
        sent_to: {
            nickname: to_nickname,
            hash: to_hash,
        }
    });

    textbox.val(""); // clear the chat bar after submitting.
    return false; // to avoid the form from submitting.
}

$("#online_section").on('click', 'a', function() {
    // open up a new chat window when you click on a users name.
    var nickname = $(this).text();
    var hash = $(this).attr("data-hash");
    
    if($("#" + hash).length == 0) {
        // don't make duplicate chatboxes for the same user.
        make_new_chat(hash, nickname);
    }
    return false;
});
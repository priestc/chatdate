setInterval(function() {
    // short poll to let the back end know this user is still available for chat
    // TODO: maybe tie this into the socketio?
    $.get(short_poll_url);
}, 30000);

function add_to_chatbox(data) {
    // Add a message coming back from the server to the chatbox.
    // 'data' is the raw payload from socketio.

    var item = $("<li>");
    if(data.type == 'chat') {
        var n = data.nickname;
        var line = "<span class='chat-message chat-message-" + n + "'>&lt;" + n + "&gt;</span> " + data.message
        item.html(line);
    } else if (data.type == 'event') {
        item.html("<span class='chat_event'>" + data.message + "</span>")
    }
    $("ul#chats").append(item);
    $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);
}

function switch_to_chat(nickname) {
    $("#chat_section").show();
    $("#user_choices").hide();
    $("#chat_title").text("Chatting with " + nickname);
}

function switch_to_selection() {
    $("#chat_section").hide();
    $("#user_choices").show();
    $("#chat_title").text("Pick a chat partner");
}

var socket = new io.Socket();
socket.connect();
socket.on('connect', function() {
    socket.subscribe('chat://' + email);
});
socket.on('message', function(data) {
    console.log("got message", data);
    if(data.type == 'confirm') {
        // message coming in to confirm that user wants to chat.
        $("#chat_section").show();
        var dual_channel = [data.who_confirmed_email, email].sort().join('/')
        socket.subscribe("chat://" + dual_channel)
        switch_to_chat(data.who_confirmed_nickname);
    } else if (data.type == 'request') {
        // incoming chat request
        result = confirm(data.from_nickname + " wants to chat with you");
        if(result) {
            // send confirmation and connect
            socket.send({
                type: 'confirm',
                requesting_email: data.from_email,
                who_confirmed_email: email,
                who_confirmed_nickname: nickname
            })
            var dual_channel = [data.from_email, email].sort().join('/')
            socket.subscribe("chat://" + dual_channel);
            switch_to_chat(data.from_nickname);
        }
    } else if (data.type == 'event') {
        // event occured!
        if(data.new_status) {
            add_to_chatbox({
                type: 'event',
                message: "Your relationship has been upgraded to level " + data.new_status,
            });
        }
    } else if (data.type == 'chat') {
        // a regular chat message came in.
        add_to_chatbox({
            type: 'chat',
            nickname: data.sent_by_nickname,
            message: data.message
        });
    }
});

$("#chatbar").submit(function() {
    // adding a new line to the chat
    var textbox =  $("#chatbar input[type=text]");
    var message = textbox.val();
    if(!message) {
        return false
    }
    var data = {
        type: 'chat',
        message: message,
        sent_by_nickname: nickname,
        sent_by_email: email
    };
    socket.send(data);
    textbox.val("");
    return false;
});

$(".potential_chat_user a").click(function() {
    // send off a request a chat with a user
    socket.send({
        type: 'request',
        to: $(this).attr('data-email'),
        from_email: email,
        from_nickname: nickname
    });
    var div = $(this).parent()
    div.addClass("request-sent");
    div.append("<span>Chat request sent to " + $(this).text() + "</span>");
    $(this).hide();
    return false;
});
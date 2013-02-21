function update_rep(new_value) {
    $.getJSON(karma_url, function(data) {
        $(".my_rep").text(data);
    });
}

function make_new_online_user(user) {
    if($("#selection_" + user.hash).length > 0) {
        return; // avoid creating duplicates
    }
    if($("#chat_" + user.hash).length >= 1) {
        // show "Re-connected" in the chat box, but only if their window is
        // already open
        add_to_chatbox({
            sent_to: {hash: my_hash},
            sent_by: {hash: user.hash},
            payload: {'connection': "Reconnected"}
        });
        $("#chat_" + user.hash).removeClass("disabled");
    }
    new_user = $("#user_template").clone();
    new_user.find(".nickname").text(user.nickname);
    new_user.attr('id', "selection_" + user.hash);
    new_user.find(".status").text(user.status);
    new_user.find(".age").text("Age: " + user.age);
    new_user.find(".rep").text(user.reputation);

    if(user.gender == 'F') {
        new_user.addClass('female');
    } else {
        new_user.addClass('male');
    }
    $("#online_section").append(new_user);
}

function remove_online_user(user) {
    $("#selection_" + user.hash).remove(); // remove from online users list
    if($("#chat_" + user.hash).length >= 1) {
        // show "disconnected" in the chat box
        add_to_chatbox({
            sent_to: {hash: my_hash},
            sent_by: {hash: user.hash},
            payload: {'connection': "Disconnected"}
        });
        $("#chat_" + user.hash).addClass("disabled");
    }
}

function add_to_chatbox(data) {
    // Add a message coming back from the server to the chatbox.
    // 'data' is the raw payload from socketio. The chat message can either
    // be from me or the other person. It can be a chat or an event.

    var chat_hash = data.sent_by.hash;
    if(data.sent_by.hash == my_hash) {
        chat_hash = data.sent_to.hash;
    }
    var chat_container = $("#chat_" + chat_hash);
    if(chat_container.length == 0) {
        // this chat messag has come from a new user. Make a new box.
        make_new_chat(data.sent_by.hash, data.sent_by.nickname);
        chat_container = $("#chat_" + chat_hash);
    }

    $.each(data.payload, function(key, value) {
        var li = $("<li>");
        if(key == 'chat') {
            // regular chat message
            var n = data.sent_by.nickname;
            var line = "<span class='chat-message chat-message-" + n + "'>&lt;" + n + "&gt;</span> " + value;
            li.html(line);
        } else if (key == 'event') {
            var message;
            if (value.relationship_status) {
                message = "You relationship has been upgraded to " + value.relationship_status + "!";
                rep_increase = "+" + value.rep_increase
                update_rep();
            } else {
                message = value;
            }
            li.html("<span class='chat_event'>" + message + "</span> <span class='rep_added'>" + rep_increase + "</span>");
        } else if (key == 'connection') {
            // disconnect or reconnect event
            li.html("<span class='connection_event'>" + value + "</span>");
        }
        var timestamp = (new Date()).toLocaleTimeString();
        li.html("<span class='chat_timestamp'>" + timestamp + "</span> " + li.html());
        chat_container.find("ul").append(li);
    });

    var chatbox = chat_container.find(".chatbox");
    chatbox.scrollTop(chatbox[0].scrollHeight);
}

function make_new_chat(hash, nickname) {
    // make a new chatbox, and bind the sending events.

    $("#chat_section").show();

    var chat_element = $("#chat_" + hash);
    if(chat_element.length) {
        chat_element.show();
    } else {
        var new_chatbox = $("#chat_template").clone().attr("id", "chat_" + hash);
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
    var chatbox =  $('#chat_' + to_hash);
    var textbox = chatbox.find("input[type=text]");
    var message = textbox.val();

    if(!message) {
        return false
    }

    var msg = {
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
    }
    socket.emit("message", msg);

    textbox.val(""); // clear the chat bar after submitting.
    return false; // to avoid the form from submitting.
}

$("#online_section").on('click', 'a', function() {
    // open up a new chat window when you click on a users name.
    var nickname = $(this).text();
    var hash = $(this).parent().attr("id").substr(10);
    
    if($("#chat_" + hash).length == 0) {
        // don't make duplicate chatboxes for the same user.
        make_new_chat(hash, nickname);
    }
    return false;
});
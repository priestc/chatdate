function update_rep() {
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
    new_user.addClass("users");
    new_user.find(".nickname").text(user.nickname).attr("data-hash", user.hash);
    new_user.attr('id', "selection_" + user.hash);
    new_user.find(".status").text(user.status);
    new_user.find(".location").text(user.location);
    new_user.find(".age").text(user.age);
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

    var partner_hash = data.sent_by.hash;
    if(data.sent_by.hash == my_hash) {
        partner_hash = data.sent_to.hash;
    }

    var chat_container = $("#selection_" + partner_hash)
    var parent_id = chat_container.parent().attr("id");

    if(parent_id == "online_section") {
        // this chat message has come from a new user. Convert them into a
        // chat box.
        convert_to_chat(data.sent_by.hash, data.sent_by.nickname);
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

function send_chat_message(to_hash, to_nickname, message) {
    // Add a new line to the chat when the "send" button is pressed or
    // enter key is pressed. This function gets binded to new chatboxes when
    // they are created

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
}

function convert_to_chat(hash, nickname) {
    // convert an "online users" box to a chat box.

    box = $("#selection_" + hash);
    box.appendTo($("#chat_section"));
    
    box.find("form").submit(function(event) {
        // when the user types something into the chatbar, send it off to the
        // user.
        var textbox = $(this).find("input[type=text]");
        var message = textbox.val();
        send_chat_message(hash, nickname, message);
        textbox.val("");
        return false;
    });
    return false;
}

$("#online_section").on('click', 'a', function() {
    // convert the "online user" box to a chat box.
    var t = $(this);
    var nickname = t.text();
    var hash = t.attr("data-hash");
    convert_to_chat(hash, nickname);
});
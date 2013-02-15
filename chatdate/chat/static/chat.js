function update_rep(new_value) {
    $(".rep").text(new_value);
}

function make_new_online_user(user) {
    if($("#selection_" + user.hash).length > 0) {
        return; // avoid creating duplicates
    }
    new_user = $("#user_template").clone();
    new_user.find(".nickname").text(user.nickname);
    new_user.attr('id', "selection_" + user.hash);
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
    } else {
        console.log("no disconnected message because no window");
    }
}

var socket = new io.Socket();
socket.connect();
socket.on('connect', function() {
    // through this channel I will send and recieve all chat messages.
    // and maybe possibly other things.
    socket.subscribe(my_hash);
});
socket.on('message', function(data) {
    //console.log("got message: ", data);
    if(data.new_user) {
        console.log("new user: ", data.new_user);
        make_new_online_user(data.new_user);
    } else if(data.remove_user) {
        console.log("remove user: ", data.remove_user);
        remove_online_user(data.remove_user);
    } else if (data.online_and_nearby) {
        console.log("all users: ", data.online_and_nearby);
        $.each(data.online_and_nearby, function(i, user) {
            make_new_online_user(user);
        });
    } else {
        add_to_chatbox(data);
    }
});

$(window).bind("beforeunload", function() { 
    socket.disconnect();
});

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
        chat_container.find("ul").append(li);
    });

    var chatbox = chat_container.find(".chatbox");
    chatbox.scrollTop(chatbox[0].scrollHeight);
}

function make_new_chat(hash, nickname) {
    // make a new chatbox, and bind the sending events.

    $("#chat_section").show();

    var chat_element = $("#chat_" + channel);
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
    socket.send(msg);

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
$("#profile_link").click(function() {
    $("#relationships_section").hide();
    $("#profile_section").show();
    $("#online_section").hide();
    return false;
});

$("#relationships_link").click(function() {
    $("#relationships_section").show();
    $("#profile_section").hide();
    $("#online_section").hide();
    return false;
});

$("#online_link").click(function() {
    $("#relationships_section").hide();
    $("#profile_section").hide();
    $("#online_section").show();
    return false;
});

function add_relationship(data) {
    var r = $("#relationship_template").clone();
    r.attr('id', data.id);
    r.find(".name").text(data.name);
    r.find(".status").text(data.status);
    $("#relationship_section").append(r);
}

function update_relationships() {
    $.getJSON(relationship_url, function(relationships) {
        $(".relationship").remove();
        $.each(relationships, function(relationship) {
            add_relationship(relationship);
        });
    });
}
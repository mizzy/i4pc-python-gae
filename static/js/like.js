function Like() {
    this.liked = {};
}

Like.prototype.action = function(media_id) {
    var elem = $('#like_icon_' + media_id);
    var klass = elem.attr('class');

    if ( klass == 'like_icon' ) {
        $.get('/like/' + media_id, function (data) {
            var count = $('#like_count_' + media_id).text();
            count++;
            $('#like_count_' + media_id).text(count);
            elem.attr('class', 'liked_icon');
            $('#like_div_' + media_id).attr('class', 'like liked');
        });
    }
    else {
        $.get('/unlike/' + media_id, function (data) {
            var count = $('#like_count_' + media_id).text();
            count--;
            $('#like_count_' + media_id).text(count);
            elem.attr('class', 'like_icon');
            $('#like_div_' + media_id).attr('class', 'like');
        });
    }
};

Like.prototype.change_icon = function() {
    for ( var i in this.liked ) {
        if ( this.liked[i] == 1 ) {
            $('#like_icon_' + i).css('background','#ff3c9a url(/img/icon.png) no-repeat 0 0');
        }
    }
};

var like = new Like();

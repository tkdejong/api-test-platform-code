import $ from 'jquery';

function wrap(id) {
    return $.map(id, function (val, i) {
        return $(val);
    });
}

var obj = wrap($(".starting"));
var pro = wrap($(".progressbar"));
var proInd = wrap($(".progressbar-indicator"));
var statusLabel = wrap($(".statuslabel"));

function update() {
    for (let i = 0; i < obj.length; i++) {
        $.ajax({
            url: window.url + obj[i].attr(window.attr_name) + '/',
            success: (data, textStatus, jqXHR) => {
                var session = data;
                if (session[window.percentage]) {
                    pro[i].css('width', `${session[window.percentage]}%`);
                    proInd[i].text(session[window.percentage] + '%');
                    statusLabel[i].text(session[window.status]);
                    // if (session[window.percentage] < 100) setTimeout(() => {
                    //     toUpdate=true
                    // }, 2000);
                    if (session[window.percentage] == 100) {
                        setTimeout(() => {
                            location.reload();
                        }, 500);
                    }
                }
            }
        })
    }
    setTimeout(() => {
        update()
    }, 2000);
}

if (obj.length > 0)
    setTimeout(update, 500)


console.log(window.url)

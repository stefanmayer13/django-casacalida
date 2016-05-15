
$('#menu_login')
    .popup({
        on: 'hover',
        addTouchEvents: 'true',
        position: 'bottom right',
        hoverable: true,
        delay: {
            show: 100,
            hide: 500
        }
    });

$('#menu_login a').on('click', function (e) {e.preventDefault();});
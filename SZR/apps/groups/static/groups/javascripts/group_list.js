function listGroupDropdown(_this) {
    const activeClass = "active";
    const submenuClass = ".list-group-submenu";
    const loaderClass = "group-loader";
    const loadUrl = "load-data-url";
    const submenu = _this.next(submenuClass);

    if (isActive()) {
        listGroupSlideUp();
    } else {
        if (!isLoaded()) {
            if (!isLoading()) {
                loadSubgroupHtml();
            }
        } else {
            listGroupSlideDown();
        }
    }

    function isActive() {
        return _this.hasClass(activeClass);
    }

    function listGroupSlideUp() {
        _this.removeClass(activeClass);
        _this.next(submenuClass).slideUp(200);
    }

    function listGroupSlideDown() {
        _this.addClass(activeClass);
        _this.next(submenuClass).slideDown(200);
    }

    function isLoaded() {
        return !isEmptyInnerHtml(submenu)
    }

    function isEmptyInnerHtml(_this) {
        return _this.html().trim().length === 0;
    }

    function isLoading() {
        return _this.hasClass(loaderClass);
    }

    function loadSubgroupHtml() {
        setLoadingClass();

        $.ajax({
            url: getLeadUrl(),
            dataType: 'html',
            success: insertSubgroupHtmlAndSlideDown
        });
    }

    function setLoadingClass() {
        _this.addClass(loaderClass);
    }

    function removeLoadingClass() {
        _this.removeClass(loaderClass);
    }

    function getLeadUrl() {
        return _this.next(submenuClass).attr(loadUrl);
    }

    function insertSubgroupHtmlAndSlideDown(html) {
        removeLoadingClass();
        submenu.html(html);
        listGroupSlideDown();
    }
}

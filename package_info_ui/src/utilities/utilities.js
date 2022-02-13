
export const removeHttp = (url) => {
    return url.replace("https://", "").replace("http://", "").replace("www.", "");
}

export const mapDistroToBootstrapColor = (distro) => {
    if (distro.startsWith("Ubuntu")) {
        return "warning";
    }
    
    if (distro.startsWith("Debian")) {
        return "danger";
    }
    
    if (distro.startsWith("Kali")) {
        return "dark";
    }

    if (distro.startsWith("Fedora")) {
        return "primary";
    }

    if (distro.startsWith("CentOS")) {
        return "info";
    }
}
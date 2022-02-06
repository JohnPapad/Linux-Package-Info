
export const removeHttp = (url) => {
    return url.
        replace("https://", "").
        replace("http://", "").
        replace("www.", "");
}
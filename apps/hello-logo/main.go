package main

import (
    "net/http"
)
func HelloLogo(w http.ResponseWriter, r *http.Request) {
        http.ServeFile(w, r, "./logo.png" )
   }

func HelloAscii(w http.ResponseWriter, r *http.Request) {
        http.ServeFile(w, r, "./logo.ascii" )
   }

func main() {

    http.HandleFunc("/", HelloLogo)
    http.HandleFunc("/ascii", HelloAscii)
    http.ListenAndServe(":8080", nil)
}

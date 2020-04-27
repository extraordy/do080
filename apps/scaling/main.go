package main

import (
	"fmt"
        "net/http"
	"os"
)
func hostname(w http.ResponseWriter, r *http.Request) {
    name, err := os.Hostname()
    if err != nil {
      panic(err)
    }
   fmt.Fprintf(w, "Hello, the applications is being served by pod: %s!", name)
   }

func main() {
  http.HandleFunc("/", hostname)
  http.ListenAndServe(":8080", nil)
}

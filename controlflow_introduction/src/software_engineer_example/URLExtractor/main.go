package main

import (
	"fmt"
	"net/url"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run main.go <URL>")
		return
	}

	inputURL := os.Args[1]
	parsedURL, err := url.Parse(inputURL)
	if err != nil || parsedURL.Scheme == "" || parsedURL.Host == "" {
		fmt.Println("Invalid URL")
		return
	}

	fmt.Println("Domain:", parsedURL.Host)
}

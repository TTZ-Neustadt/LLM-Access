# Install once: install.packages(c("ellmer", "httr2"))
# Put configuration in your user .Renviron, restart R, then run this file.
library(ellmer)
library(httr2)

base_url <- sub("/+$", "", Sys.getenv("OPENAI_BASE_URL"))
if (!nzchar(base_url)) stop("Set OPENAI_BASE_URL first.")
key <- Sys.getenv("OPENAI_API_KEY")
if (!nzchar(key)) stop("Set OPENAI_API_KEY in your .Renviron and restart R.")

models <- request(paste0(base_url, "/models")) |>
  req_auth_bearer_token(key) |>
  req_timeout(60) |>
  req_perform() |>
  resp_body_json()
model_ids <- vapply(models$data, function(x) x$id, character(1))
print(model_ids)
model <- Sys.getenv("OPENAI_MODEL")
if (!nzchar(model) || !model %in% model_ids) {
  stop("Set OPENAI_MODEL to one of the model IDs printed above and run again.")
}
if (!"chat_openai_compatible" %in% getNamespaceExports("ellmer")) {
  stop("Update ellmer: install.packages('ellmer'), then restart R.")
}

# Keep this shared instruction identical across students for prefix-cache reuse.
system_prompt <- "You help analyse short survey responses. Be concise, follow the requested format, and do not invent details."
new_chat <- function(echo = "none") {
  chat_openai_compatible(
    base_url = base_url,
    credentials = function() key,
    model = model,
    system_prompt = system_prompt,
    echo = echo
  )
}

# A reusable object retains conversation history. Output appears as it streams.
chat <- new_chat(echo = "output")
invisible(chat$chat("Explain sentiment classification in two sentences."))

# Use a fresh chat for each independent survey response.
responses <- c(
  "The course was useful, but I wanted more time for exercises.",
  "The examples were clear and I enjoyed the practical sessions."
)
for (response in responses) {
  summary <- new_chat()$chat(paste("Summarise this survey response in one sentence:", response))
  label <- new_chat()$chat(paste(
    "Classify sentiment. Reply with only positive, negative, mixed, or neutral.",
    "Survey response:", response
  ))
  cat("\nResponse:", response, "\nSummary:", summary, "\nLabel:", label, "\n")
}

## These exports are based on the F12 Network tab in Microsoft Edge, and the API calls made by the Spond web app to Spond Club.

$bearerToken = read-host -Prompt "Enter your Spond Bearer Token"

$clubId = "$($clubId)"

## Get all members 
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
$members = Invoke-WebRequest -UseBasicParsing -Uri "https://api.spond.com/club/v1/members?" `
  -WebSession $session `
  -Headers @{
  "authority"              = "api.spond.com"
  "method"                 = "GET"
  "path"                   = "/club/v1/members?"
  "scheme"                 = "https"
  "accept"                 = "application/json"
  "accept-encoding"        = "gzip, deflate, br, zstd"
  "accept-language"        = "en-GB,en;q=0.9,en-US;q=0.8"
  "api-level"              = "4.72.0"
  "authorization"          = "$($BearerToken)"
  "cache-control"          = "no-cache"
  "origin"                 = "https://club.spond.com"
  "pragma"                 = "no-cache"
  "priority"               = "u=1, i"
  "referer"                = "https://club.spond.com/"
  "sec-ch-ua"              = "`"Not;A=Brand`";v=`"99`", `"Microsoft Edge`";v=`"139`", `"Chromium`";v=`"139`""
  "sec-ch-ua-mobile"       = "?0"
  "sec-ch-ua-platform"     = "`"Windows`""
  "sec-fetch-dest"         = "empty"
  "sec-fetch-mode"         = "cors"
  "sec-fetch-site"         = "same-site"
  "x-spond-clubid"         = "$($clubId)"
  "x-spond-membershipauth" = "undefined"
} `
  -ContentType "application/json"

## List Payments

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
$payments = Invoke-WebRequest -UseBasicParsing -Uri "https://api.spond.com/club/v1/payments/?" `
  -WebSession $session `
  -Headers @{
  "authority"              = "api.spond.com"
  "method"                 = "GET"
  "path"                   = "/club/v1/payments/?"
  "scheme"                 = "https"
  "accept"                 = "application/json"
  "accept-encoding"        = "gzip, deflate, br, zstd"
  "accept-language"        = "en-GB,en;q=0.9,en-US;q=0.8"
  "api-level"              = "4.72.0"
  "authorization"          = "$($BearerToken)"
  "cache-control"          = "no-cache"
  "origin"                 = "https://club.spond.com"
  "pragma"                 = "no-cache"
  "priority"               = "u=1, i"
  "referer"                = "https://club.spond.com/"
  "sec-ch-ua"              = "`"Not;A=Brand`";v=`"99`", `"Microsoft Edge`";v=`"139`", `"Chromium`";v=`"139`""
  "sec-ch-ua-mobile"       = "?0"
  "sec-ch-ua-platform"     = "`"Windows`""
  "sec-fetch-dest"         = "empty"
  "sec-fetch-mode"         = "cors"
  "sec-fetch-site"         = "same-site"
  "x-spond-clubid"         = "$($clubId)"
  "x-spond-membershipauth" = "undefined"
} `
  -ContentType "application/json"

## List specific payment details - recipients and status

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
$paymentDetails = Invoke-WebRequest -UseBasicParsing -Uri "https://api.spond.com/club/v1/payments/627E3CC0A78840FC8A15B076766935F7?includeSignupRequestRecipients=false" `
  -WebSession $session `
  -Headers @{
  "authority"              = "api.spond.com"
  "method"                 = "GET"
  "path"                   = "/club/v1/payments/66297C063E18413DAD30E045DE7157EA?includeSignupRequestRecipients=false"
  "scheme"                 = "https"
  "accept"                 = "application/json"
  "accept-encoding"        = "gzip, deflate, br, zstd"
  "accept-language"        = "en-GB,en;q=0.9,en-US;q=0.8"
  "api-level"              = "4.72.0"
  "authorization"          = "$($BearerToken)"
  "cache-control"          = "no-cache"
  "origin"                 = "https://club.spond.com"
  "pragma"                 = "no-cache"
  "priority"               = "u=1, i"
  "referer"                = "https://club.spond.com/"
  "sec-ch-ua"              = "`"Not;A=Brand`";v=`"99`", `"Microsoft Edge`";v=`"139`", `"Chromium`";v=`"139`""
  "sec-ch-ua-mobile"       = "?0"
  "sec-ch-ua-platform"     = "`"Windows`""
  "sec-fetch-dest"         = "empty"
  "sec-fetch-mode"         = "cors"
  "sec-fetch-site"         = "same-site"
  "x-spond-clubid"         = "$($clubId)"
  "x-spond-membershipauth" = "undefined"
} `
  -ContentType "application/json"


## Download CSV of payment

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
Invoke-WebRequest -UseBasicParsing -Uri "https://api.spond.com/club/v1/payments/66297C063E18413DAD30E045DE7157EA/export" `
  -Method "POST" `
  -WebSession $session `
  -Headers @{
  "authority"              = "api.spond.com"
  "method"                 = "POST"
  "path"                   = "/club/v1/payments/627E3CC0A78840FC8A15B076766935F7/export"
  "scheme"                 = "https"
  "accept"                 = "application/json"
  "accept-encoding"        = "gzip, deflate, br, zstd"
  "accept-language"        = "en-GB,en;q=0.9,en-US;q=0.8"
  "api-level"              = "4.72.0"
  "authorization"          = "$($BearerToken)"
  "cache-control"          = "no-cache"
  "origin"                 = "https://club.spond.com"
  "pragma"                 = "no-cache"
  "priority"               = "u=1, i"
  "referer"                = "https://club.spond.com/"
  "sec-ch-ua"              = "`"Not;A=Brand`";v=`"99`", `"Microsoft Edge`";v=`"139`", `"Chromium`";v=`"139`""
  "sec-ch-ua-mobile"       = "?0"
  "sec-ch-ua-platform"     = "`"Windows`""
  "sec-fetch-dest"         = "empty"
  "sec-fetch-mode"         = "cors"
  "sec-fetch-site"         = "same-site"
  "x-spond-clubid"         = "$($clubId)"
  "x-spond-membershipauth" = "undefined"
} `
  -ContentType "application/json" `
  -Body "[`"768BE0CDE94F48429E87DFA05713853D`",`"D39E5D5D76A14C85B16FEE5C307DF20E`",`"BB5F13F8AC3745F1BE2862F96D2D56C0`",`"A7F623B874A947639368BC4CF9E8E344`",`"16AF18179E234870BD40DD72DA2E4E61`",`"429E1B673EA34618B5E5AE60929E8D0B`",`"46662C17BCF04916AC4B3535F6A11CA0`",`"584282EA1EC54D23846F5A97FC1DC2AE`",`"AFCE028BBEA74C80B74CE9A2ABA642D9`",`"3D47BCA74435460895FAAB454228B98F`",`"F274DBA9AD8E4CFCB55A952D9EF76A02`"]"
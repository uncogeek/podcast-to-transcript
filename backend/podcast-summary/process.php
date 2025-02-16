<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['fileUrl'])) {
    $fileUrl = $_POST['fileUrl'];
    $prompt = isset($_POST['prompt']) ? trim($_POST['prompt']) : '';

    // Validate URL
    if (!filter_var($fileUrl, FILTER_VALIDATE_URL)) {
        echo json_encode(['success' => false, 'error' => 'Invalid URL']);
        exit;
    }

    // Initialize cURL session to fetch file content
    $ch = curl_init($fileUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_MAXREDIRS, 5);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);

    // Execute cURL session and get the file content
    $content = curl_exec($ch);

    // Check for cURL errors
    if (curl_errno($ch)) {
        echo json_encode(['success' => false, 'error' => 'Failed to download file: ' . curl_error($ch)]);
        exit;
    }

    // Close cURL session
    curl_close($ch);

    // Construct the base prompt
    $basePrompt = "Summarize the following podcast transcript in a detailed yet concise manner:

1. Create a clear heading based on the main subject/theme of the podcast
2. Do not change the language of the content after summarizing
3. Use headings, subheadings, and markdown for clear formatting
4. Ensure all key points, quotes, and important discussions remain intact
5. Preserve significant anecdotes, examples, and expert insights
6. Use bullet points where appropriate
7. Highlight key concepts and memorable quotes with bold text
8. Explain details comprehensively while avoiding repetition
9. Structure the summary for easy reading with clear topic transitions
10. Include any relevant statistics, data, or research mentioned
11. Note any significant guest speakers or expert contributors
12. If the content is in Persian, summarize it in Persian
13. If the content is in English, summarize it in English

The summary should capture the essence of the discussion while maintaining the natural flow of conversation and key takeaways.";

    if (!empty($prompt)) {
        $basePrompt .= "\n\n" . $prompt;
    }

    $finalPrompt = $basePrompt . "\n\nContent:\n" . $content;

    try {
        $apiKey = 'API-KEY'; // Replace with your actual OpenAI API key
        $url = 'https://api.host.domain/v1/chat/completions'; // Replace with your OpenAI or custom provider endpoint e.g. https://api.openai.com/v1/chat/completions

        $data = array(
            'model' => 'gpt-4o',
            'messages' => [
                ['role' => 'system', 'content' => 'You are a helpful assistant that summarizes content.'],
                ['role' => 'user', 'content' => $finalPrompt]
            ],
            'max_tokens' => 4096,
            'temperature' => 0.7,
        );

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            'Content-Type: application/json',
            'Authorization: Bearer ' . $apiKey
        ));

        $response = curl_exec($ch);
        file_put_contents('api_response.log', $response . "\n\n", FILE_APPEND);

        if ($response === false) {
            throw new Exception(curl_error($ch), curl_errno($ch));
        }

        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        if ($httpCode !== 200) {
            throw new Exception("HTTP Error: $httpCode");
        }

        curl_close($ch);

        $responseBody = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("JSON decode error: " . json_last_error_msg());
        }

        if (!isset($responseBody['choices'][0]['message']['content'])) {
            throw new Exception("Unexpected API response structure");
        }

        echo json_encode([
            'success' => true,
            'summary' => trim($responseBody['choices'][0]['message']['content']),
        ]);

    } catch (Exception $e) {
        echo json_encode([
            'success' => false,
            'error' => 'Failed to get summary.',
            'message' => $e->getMessage(),
        ]);
    }
} else {
    echo json_encode(['success' => false, 'error' => 'Invalid request.']);
}

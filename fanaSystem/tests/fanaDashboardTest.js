const PUBLIC_IP = "internals.getfana.com";  // Your public IP or domain
const BASE_URL = `https://${PUBLIC_IP || 'localhost:8000'}`;
const AUTH_SERVER_LOGIN_URL = `${BASE_URL}/fanaAuthenticator/api/token/`;
const WSL_SERVER_URL = `wss://${PUBLIC_IP || 'localhost:8000'}/ws/dashboard/`;
const SEND_ORDER_TO_DASHBOARD_URL = `${BASE_URL}/fanaDashboard/receiveOrder/`;

// Constants for order details and table information
const USERNAME = "valid_username";
const PASSWORD = "valid_password";
const ORDER_ID = "order_123";
const DEVICE_ID = "device_123";
const TABLE_ID = "table_1";

let access_token = null;
let order_reflected = false;
let fana_call_reflected = false;
let ws = null;

// Helper function to get JWT token
async function getJwtToken() {
    try {
        console.log("[INFO] Getting JWT token...");
        const response = await fetch(AUTH_SERVER_LOGIN_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: USERNAME, password: PASSWORD }),
        });

        if (response.ok) {
            const tokens = await response.json();
            access_token = tokens.access;
            console.log("[INFO] JWT Token acquired:", tokens);
            return tokens;
        } else {
            const error = await response.json();
            console.error("[ERROR] Failed to acquire JWT token:", error);
            return null;
        }
    } catch (error) {
        console.error("[ERROR] Error getting JWT token:", error);
        return null;
    }
}

// WebSocket Listener function
function websocketListener(stopEvent) {
    ws.onmessage = (event) => {
        const result = event.data;
        if (!result.trim()) {
            console.log("[INFO] Received an empty WebSocket message. Ignoring...");
            return;
        }

        console.log("[INFO] WebSocket event received:", result);
        try {
            const eventData = JSON.parse(result);
            if (eventData.message_type === "order_update" && eventData.order_id === ORDER_ID) {
                console.log("[INFO] Order reflected on dashboard.");
                order_reflected = true;
            }

            if (eventData.message_type === "table_state" && eventData.table_id === TABLE_ID) {
                console.log("[INFO] Fana call reflected on dashboard.");
                fana_call_reflected = true;
            }
        } catch (error) {
            console.error("[ERROR] Failed to decode WebSocket message:", error);
        }
    };
}

// Function to send an order
async function sendOrder() {
    try {
        console.log("[INFO] Sending order...");
        const response = await fetch(SEND_ORDER_TO_DASHBOARD_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`,
            },
            body: JSON.stringify({
                order_id: ORDER_ID,
                order_details: {
                    items: [
                        { name: "Burger", cost: 100, quantity: 2, itemTotal: 200 },
                        { name: "Fries", cost: 50, quantity: 1, itemTotal: 50 },
                    ],
                    totalAmount: 250,
                },
            }),
        });

        const data = await response.json();
        console.log("[INFO] Send Order Response:", data);
        return response.ok && data.status === "success";
    } catch (error) {
        console.error("[ERROR] Error sending order:", error);
        return false;
    }
}

// Function to handle Fana call
async function handleFanaCall() {
    try {
        console.log("[INFO] Sending Fana call...");
        const response = await fetch(`${BASE_URL}/fanaDashboard/handleFanaCall/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`,
            },
            body: JSON.stringify({
                table_id: TABLE_ID,
                state: "calling",
                time_taken: 1000,
            }),
        });

        const data = await response.json();
        console.log("[INFO] Handle Fana Call Response:", data);
        return response.ok && data.status === "success";
    } catch (error) {
        console.error("[ERROR] Error sending Fana call:", error);
        return false;
    }
}

// Main Test Function
async function testSequence() {
    try {
        // Step 1: Get JWT Token
        const tokens = await getJwtToken();
        if (!tokens) {
            console.error("[ERROR] Test failed: Unable to acquire JWT token.");
            console.log("Result: FAILED");
            return;
        }

        // Step 2: Connect to WebSocket
        console.log("[INFO] Connecting to WebSocket...");
        ws = new WebSocket(WSL_SERVER_URL, [], {
            headers: { "Authorization": `Bearer ${access_token}` },
        });

        ws.onopen = () => {
            console.log("[INFO] WebSocket connected.");
            // Start the listener for WebSocket events
            websocketListener();
        };

        ws.onerror = (error) => {
            console.error("[ERROR] WebSocket connection failed:", error);
        };

        ws.onclose = () => {
            console.log("[INFO] WebSocket connection closed.");
        };

        // Step 3: Send Order
        if (!(await sendOrder())) {
            console.error("[ERROR] Test failed: Order not sent successfully.");
            ws.close();
            console.log("Result: FAILED");
            return;
        }

        await new Promise(resolve => setTimeout(resolve, 2000));  // Allow some time for the dashboard to process

        // Step 4: Send Fana Call
        if (!(await handleFanaCall())) {
            console.error("[ERROR] Test failed: Fana call not sent successfully.");
            ws.close();
            console.log("Result: FAILED");
            return;
        }

        await new Promise(resolve => setTimeout(resolve, 2000));  // Allow time for WebSocket events to be received

        // Step 5: Validate WebSocket Events
        console.log("[INFO] Verifying WebSocket events...");
        if (!order_reflected) {
            console.error("[ERROR] Order not reflected on dashboard.");
        }
        if (!fana_call_reflected) {
            console.error("[ERROR] Fana call not reflected on dashboard.");
        }

        // Final Test Result
        if (order_reflected && fana_call_reflected) {
            console.log("Result: PASSED");
        } else {
            console.log("Result: FAILED");
        }
    } catch (error) {
        console.error("[ERROR] Test failed with exception:", error);
        console.log("Result: FAILED");
    } finally {
        // Close the WebSocket connection
        if (ws) {
            ws.close();
        }
    }
}

// Run the Test
testSequence();

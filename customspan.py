from flask import Flask, request, jsonify  
from opentelemetry import trace  
from opentelemetry.sdk.trace import TracerProvider  
from opentelemetry.sdk.trace.export import BatchSpanProcessor  
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter  
from opentelemetry.instrumentation.flask import FlaskInstrumentor  
  
# REPLACE with your real Azure Application Insights CONNECTION STRING!  
CONNECTION_STRING = "InstrumentationKey=f4e4cda2-0b5b-43a8-b108-4f5b64ea0845;IngestionEndpoint=https://australiaeast-1.in.applicationinsights.azure.com/;LiveEndpoint=https://australiaeast.livediagnostics.monitor.azure.com/;ApplicationId=f3203ea2-b532-4b13-a72c-ba5afb4f3fd8"  
  
trace.set_tracer_provider(TracerProvider())  
tracer = trace.get_tracer(__name__)  
  
exporter = AzureMonitorTraceExporter(connection_string=CONNECTION_STRING)  
span_processor = BatchSpanProcessor(exporter)  
trace.get_tracer_provider().add_span_processor(span_processor)  
  
# --- 2. Set up Flask with auto-instrumentation ---  
app = Flask(__name__)  
FlaskInstrumentor().instrument_app(app)  
  
# --- 3. Demo Endpoint with Custom Spans and Attributes ---  
@app.route("/submit-proposal", methods=["POST"])  
def submit_proposal():  
    user_id = request.json.get("user_id", "unknown_user")  
    proposal_id = request.json.get("proposal_id", "no_id")  
  
    with tracer.start_as_current_span("ProposalSubmission") as span:  
        # Custom attributes for easier search/filter in telemetry  
        span.set_attribute("user.id", user_id)  
        span.set_attribute("proposal.id", proposal_id)  
        span.set_attribute("business.operation", "proposal_submission")  
  
        # Simulate proposal validation (custom span)  
        with tracer.start_as_current_span("ValidateProposal") as validation_span:  
            validation_span.set_attribute("validation.type", "basic")  
            # Simulate a check  
            if not proposal_id:  
                validation_span.set_attribute("validation.status", "fail")  
                return jsonify({"status": "error", "message": "Proposal ID missing"}), 400  
            validation_span.set_attribute("validation.status", "pass")  
  
        # Simulate saving to DB (custom span)  
        with tracer.start_as_current_span("SaveProposal") as save_span:  
            save_span.set_attribute("db.table", "proposals")  
            save_span.set_attribute("db.action", "insert")  
            # Simulated DB operation (could raise error to test exception traces)  
            # raise Exception("Simulated DB error")  
  
        return jsonify(  
            {"status": "success", "user_id": user_id, "proposal_id": proposal_id}  
        ), 200  
  
# --- 4. Run the Flask app ---  
if __name__ == "__main__":  
    app.run(debug=True, port=5000)  

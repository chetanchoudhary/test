import json
import os
from pathlib import Path

from flask import Flask, url_for, request, jsonify, send_file, request
from flask_restful import Resource, reqparse


from models.sensor import SensorModel
from models.quickSim_history import QuickSimModel

from simulation.thingworxSim import simulationThingworx

from simulation.azureSim import simulationAZURE

from simulation.awsSim import simulationAWS


from libs import upload_support
from werkzeug.datastructures import FileStorage


class QuickSimulation(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=True, help="Please add the name of the Sensor !"
    )
    parser.add_argument("cloud", type=str, required=True,
                        help="Please add the cloud on which you want to work !")
    parser.add_argument(
        "connection", type=str, required=True, help="Please add the connection Parameters !"
    )
    parser.add_argument(
        "format", type=str, required=True, help="Please add in which format do you want to send Data !"
    )
    parser.add_argument(
        "timeInterval", type=int, required=True, help="Please add the Time Interval between data simulations !"
    )
    parser.add_argument(
        "frequency", type=int, required=True, help="Please add how many times you want to simulate the sensor Behaviour !"
    )
    parser.add_argument("payload", type=str, required=True,
                        help="Please add payload !")

    def post(self):

        data = QuickSimulation.parser.parse_args()

        history = QuickSimModel(data["name"], data["cloud"], data["connection"],
                                data["format"], data["timeInterval"], data["frequency"], data["payload"])

        try:
            history.save_to_db()
        except:
            return {"message": "An error occurred while simulation, please try again with correct parameters."}

        connectionDict = json.loads(data["connection"])
        payloadDict = json.loads(data["payload"])

        if data["cloud"] == "thingworx":
            simulationThingworx(
                connectionDict, data["frequency"], data["timeInterval"], payloadDict)
        elif data["cloud"] == "aws":
            simulationAWS(connectionDict, None,
                          data["frequency"], data["timeInterval"], payloadDict)


class UploadCertificateQuickSim(Resource):
    def post(self):

        folder = "temp"
        try:
            # save(self, storage, folder=None, name=None)
            certificate_path = upload_support.save_certificate(
                request.files['certificate'], folder=folder)
            print("File saved to: ", certificate_path)
            return {"message": "Upload Successful", "statusCode": 201}, 201
        except Exception as error:
            print(error)

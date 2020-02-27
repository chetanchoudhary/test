import json
import os
import threading
from pathlib import Path

from flask import Flask, url_for, request, jsonify, send_file, request
from flask_restful import Resource, reqparse


from models.template import TemplateModel

from simulation.thingworxSim import simulationThingworx

from simulation.azureSim import simulationAZURE

from simulation.awsSim import simulationAWS


from libs import upload_support
from werkzeug.datastructures import FileStorage


class Template(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=True, help="Please add the name of the Sensor !"
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

    def get(self):
        # Try except block and Authentication to be added
        return {"templates": list(map(lambda x: x.json(), TemplateModel.query.all()))}

    def post(self):
        # user = current_identity
        # print(user.access)

        # if user.access == "admin":
        data = Template.parser.parse_args()
        if TemplateModel.find_by_name(data["name"]):
            return {
                "message": "A template with name '{}' already exists.".format(
                    data["name"]
                )
            }

        template = TemplateModel(data["name"], data["format"], data["timeInterval"], data["frequency"], data["payload"])

        try:
            template.save_to_db()
        except:
            return {"message": "An error occurred while adding the template, please try again with correct parameters."}

        return {"message": "Template Successfully Created !", "template": template.json(), "statusCode": 201}, 201
        # else:
        #     return {"message": "You do not have ADMIN Rights"}, 405


class TemplateByName(Resource):
    # def post(self, name):
    #     sensor = SensorModel.find_by_name(name)
    #     if sensor:
    #         sensor = sensor.json()
    #         connection = sensor['connection']
    #         print(connection)
    #         connectionDict = json.loads(connection)
    #         payload = sensor['payload']
    #         print(payload)
    #         print(".....................1")
    #         payloadDict = json.loads(payload)
    #         print(".....................2")            # print(connectionDict)
    #         try:
    #             if sensor['cloud'] == "thingworx":
    #                 simulationThingworx(
    #                     connectionDict, sensor['frequency'], sensor['timeInterval'], payloadDict)
    #             elif sensor['cloud'] == "aws":

    #                 simulationAWS(
    #                     connectionDict, name, sensor['frequency'], sensor['timeInterval'], payloadDict)

    #             elif sensor['cloud'] == "azure":
    #                 simulationAZURE(connectionDict)
    #             else:
    #                 return {"message": "We don't support simulation for this cloud."}

    #             return {"message": "Simulation Completed"}
    #         except Exception as error:
    #             print(error)
    #             return {"message": "Something went wrong, Please check the cloud server and try again."}
    #     else:
    #         return {"message": "Sensor Not Found"}, 404

    def get(self, name):
        template = TemplateModel.find_by_name(name)
        if template:
            return template.json(), 200
        return {"message": "Template not found", "statusCode": 404}

    def delete(self, name):
        #         user = current_identity
        #         print(user.access)

        #         if user.access == "admin":
        template = TemplateModel.find_by_name(name)
        if template:
            template.delete_from_db()
            return {"message": "Template deleted"}
        else:
            return {"message": "Template not found"}


# class UpdateSensorRange(Resource):
#     parser = reqparse.RequestParser()

#     parser.add_argument(
#         "minRange", type=int, required=True, help="This field cannot be left blank!"
#     )
#     parser.add_argument(
#         "maxRange", type=int, required=True, help="This field cannot be left blank!"
#     )

#     def put(self, name):
#         data = UpdateSensorRange.parser.parse_args()
#         sensor = SensorModel.find_by_name(name)

#         try:
#             if sensor is None:
#                 return {"message": "Sensor not Found !"}
#             else:
#                 sensor.minRange = data["minRange"]
#                 sensor.maxRange = data["maxRange"]
#                 sensor.save_to_db()
#                 return {"message": "Frequency has been updated.", "sensor": sensor.json()}
#         except Exception as error:
#             return {"message": error}


# class UpdateSensorFrequency(Resource):
#     parser = reqparse.RequestParser()

#     parser.add_argument(
#         "frequency", type=int, required=True, help="This field cannot be left blank!"
#     )

#     def put(self, name):
#         data = UpdateSensorFrequency.parser.parse_args()
#         sensor = SensorModel.find_by_name(name)
#         try:
#             if sensor is None:
#                 return {"message": "Sensor not Found !"}
#             else:
#                 sensor.frequency = data["frequency"]
#                 sensor.save_to_db()
#                 return {"message": "Frequency has been updated.", "sensor": sensor.json()}
#         except Exception as error:
#             return {"message": error}


# class UpdateSensorTimeInterval(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument(
#         "timeInterval", type=int, required=True, help="This field cannot be left blank!"
#     )

#     def put(self, name):
#         data = UpdateSensorTimeInterval.parser.parse_args()
#         sensor = SensorModel.find_by_name(name)
#         try:
#             if sensor is None:
#                 return {"message": "Sensor not Found !"}
#             else:
#                 sensor.timeInterval = data["timeInterval"]
#                 sensor.save_to_db()
#                 return {"message": "Time Interval has been updated.", "sensor": sensor.json()}
#         except Exception as error:
#             return {"message": error}


class UploadCertificate(Resource):
    def post(self, name):

        folder = f"{name}"
        try:
            # save(self, storage, folder=None, name=None)
            certificate_path = upload_support.save_certificate(
                request.files['certificate'], folder=folder)
            print("File saved to: ", certificate_path)
            return {"message": "Upload Successful", "statusCode": 201}, 201
        except Exception as error:
            return {"message": error}


class RootCAFileCheck(Resource):
    def get(self, name):
        path = Path('static/certificates/' + name + '/root-CA.crt')
        result = path.exists()
        if result == True:
            return {"message": "RootCA File Exists", "exists": True}, 200
        else:
            return {"message": "RootCA File does not Exists", "exists": False}

    def delete(self, name):
        path = Path('static/certificates/' + name + '/root-CA.crt')
        try:
            path.unlink()
            return {"message": "RootCA file Deleted."}
        except Exception as error:
            return {"message": error}


class CertificateFileCheck(Resource):
    def get(self, name):
        path = Path('static/certificates/' + name + '/' + name + '.cert.pem')
        result = path.exists()
        if result == True:
            return {"message": "Certificate File Exists", "exists": True}, 200
        else:
            return {"message": "Certificate File does not Exists", "exists": False}

    def delete(self, name):
        path = Path('static/certificates/' + name + '/' + name + '.cert.pem')
        try:
            path.unlink()
            return {"message": "Certificate file Deleted."}
        except Exception as error:
            return {"message": error}


class PrivateKeyFileCheck(Resource):
    def get(self, name):
        path = Path('static/certificates/' + name +
                    '/' + name + '.private.key')
        result = path.exists()
        if result == True:
            return {"message": "Private Key File Exists", "exists": True}, 200
        else:
            return {"message": "Private Key does not Exists", "exists": False}

    def delete(self, name):
        path = Path('static/certificates/' + name +
                    '/' + name + '.private.key')
        try:
            path.unlink()
            return {"message": "Private Key file Deleted."}
        except Exception as error:
            return {"message": error}


class TemplateSimulation(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("cloud", type=str, required=True, help="Please select a cloud.")
    parser.add_argument("connection", type=str, required=True,
                        help="Please add connection !")

    def post(self, name):
        data = TemplateSimulation.parser.parse_args()
        template = TemplateModel.find_by_name(name)
        if template:
            template = template.json()
            cloud = data["cloud"]
            connectionDict = json.loads(data["connection"])
            payloadDict = json.loads(template["payload"])
            try:
                if cloud == "thingworx":
                    simulationThingworx(
                        connectionDict, template['frequency'], template['timeInterval'], payloadDict)
                elif cloud == "aws":

                    simulationAWS(
                        connectionDict, name, template['frequency'], template['timeInterval'], payloadDict)

                elif cloud == "azure":
                    simulationAZURE(connectionDict)
                else:
                    return {"message": "We don't support simulation for this cloud."}

                return {"message": "Simulation Completed"}
            except Exception as error:
                print(error)
                return {"message": "Something went wrong, Please check the cloud server and try again."}
        else:
            return {"message": "Template not found"}, 500


class MultiThreadSimulation(Resource):
    parser = reqparse.RequestParser()
    # parser.add_argument("cloud", type=str, required=True, help="Please select a cloud.")
    parser.add_argument("connectionArray", type=str, required=True, help="Please add connection !")

    def post(self, name):
        data = MultiThreadSimulation.parser.parse_args()
        template = TemplateModel.find_by_name(name)
        if template:
            template = template.json()
            payloadDict = json.loads(template["payload"])
            frequency = template['frequency']
            timeInterval = template['timeInterval']
            print(data['connectionArray'])

            connection = json.loads(data['connectionArray'])
            print(connection) 
            connectionArray = connection['connections']   
            threads = []
            for i in range(len(connectionArray)):
                t = threading.Thread(
                    target=simulationThingworx,
                    args=[connectionArray[i], frequency, timeInterval, payloadDict],
                )
                t.start()
                threads.append(t)

            for thread in threads:
                thread.join()

            return {"message": "Simulation Completed"}



        else:
            return {"message": "Template not found"}, 500
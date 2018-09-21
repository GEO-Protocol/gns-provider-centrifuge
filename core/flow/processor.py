import logging
import struct

from core.clients.clients import Client
from core.clients.handler import ClientsHandler
from core.crypto.cipher import AESCipher
from core.messages.base import Request, Endpoint
from core.messages.common import SetAddressRequest, SetAddressAckResponse, ParticipantLookupRequest, \
    ParticipantLookupNotFoundResponse, ParticipantLookupAckResponse, ConnectionRequest
from core.messages.encrypted import EncryptedRequest, EncryptedResponse
from core.settings import DEBUG


class ProcessingResponse:
    def __init__(self, encrypted_response: EncryptedResponse, client: Client, endpoint: Endpoint):
        self._client = client
        self._endpoint = endpoint
        self._encrypted_response = encrypted_response

    @property
    def encrypted_response(self):
        return self._encrypted_response

    @property
    def client(self):
        return self._client

    @property
    def endpoint(self):
        return self._endpoint


class RequestsFlow:
    def __init__(self, clients_handler: ClientsHandler):
        self._cipher = AESCipher()
        self._clients = clients_handler

    def process(self, request: EncryptedRequest) -> [ProcessingResponse]:
        client = self._clients.get_by_id(request.client_id)
        if not client:
            return [], None, None

        message = self._decode_request(request, client)
        if not message:
            return [], None, None

        try:
            return self._process(message, client)

        except Exception as e:
            logging.error(
                f"EXCEPTION: '{e}'; "
                f"Request: {message.to_json()}")

            if DEBUG:
                raise e

            return [], None, None

    def _decode_request(self, enc_request: EncryptedRequest, client: Client) -> Request or None:
        content = self._cipher.decrypt(enc_request.data, client.secret)
        type_id, nonce = struct.unpack('>BI', content[:5])  # 1B + 4B

        if type_id == Request.Types.set_address:
            return SetAddressRequest.deserialize(content[5:], client.id, enc_request.remote_endpoint[0])

        elif type_id == Request.Types.participant_lookup:
            return ParticipantLookupRequest.deserialize(content[5:], client.id, enc_request.remote_endpoint[0])

        #
        # Other types goes here
        #

        else:
            return None

    def _process(self, message: Request, client: Client) -> [ProcessingResponse]:
        if message.type_id == Request.Types.set_address:
            return self._process_set_address(message, client)

        elif message.type_id == Request.Types.participant_lookup:
            return self._process_participant_lookup(message, client)

        #
        # Other types goes here
        #

        else:
            return None

    def _process_set_address(self, request: SetAddressRequest, client: Client) -> [ProcessingResponse]:
        self._clients.set_ipv4_address(
            client, request.remote_ipv4_address, request.port)

        ack = SetAddressAckResponse()
        enc = EncryptedResponse(self._cipher.encrypt(ack.serialize(), client.secret))
        endpoint = Endpoint(request.port, request.remote_ipv4_address)
        return [ProcessingResponse(enc, client, endpoint)]

    def _process_participant_lookup(self, request: ParticipantLookupRequest, client: Client) -> [ProcessingResponse]:
        # todo: in case if participant has more than one address -> use it sequentially.
        # (if one device responded with ack - do not ask another one)
        # (otherwise, several devices at the same time might begin to respond to the requester)

        def respond_not_found():
            not_found_response = ParticipantLookupNotFoundResponse()
            enc = EncryptedResponse(self._cipher.encrypt(not_found_response.serialize(), client.secret))
            endpoint = Endpoint(request.port, request.remote_ipv4_address)
            return [ProcessingResponse(enc, client, endpoint)]

        lookup_client = self._clients.get_by_name(request.participant_name)
        if not lookup_client:
            return respond_not_found()

        addresses_and_ports = self._clients.get_ipv4_addresses_and_ports(client.id)
        if not addresses_and_ports:
            respond_not_found()

        responses = []

        # Participant found.
        # Requester must be notified by the ack message in the first order.
        ack = ParticipantLookupAckResponse()
        enc_ack = EncryptedResponse(self._cipher.encrypt(ack.serialize(), client.secret))
        endpoint = Endpoint(request.port, request.remote_ipv4_address)
        responses.append(ProcessingResponse(enc_ack, client, endpoint))

        # Lookup participant should be notified on each one address
        for address, port in addresses_and_ports:
            request = ConnectionRequest(client.name, Endpoint(request.port, request.remote_ipv4_address))
            enc_req = EncryptedResponse(self._cipher.encrypt(request.serialize(), lookup_client.secret))
            endpoint = Endpoint(port, address)
            responses.append(ProcessingResponse(enc_req, lookup_client, endpoint))

        return responses

"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiKinesisHelper = void 0;
const databricks_1 = require("../interface/databricks");
const client_kinesis_1 = require("@aws-sdk/client-kinesis");
const util_1 = require("util");
const uuid_1 = require("uuid");
const axios_1 = __importDefault(require("axios"));
const kinesis = new client_kinesis_1.KinesisClient({
    region: 'us-east-1',
});
class ApiKinesisHelper {
    static data(item) {
        return {
            _id: item.id,
            documentKey: item.id,
            fullDocument: item.fullDocument,
            operationType: item.operationType,
            updateDescription: null,
            ns: {
                db: databricks_1.IDatabricksDb.BOT,
                coll: item.collection,
            },
        };
    }
    static putRecord(item) {
        return __awaiter(this, void 0, void 0, function* () {
            const payload = ApiKinesisHelper.data(Object.assign({ id: (0, uuid_1.v4)() }, item));
            const command = new client_kinesis_1.PutRecordCommand({
                StreamName: ApiKinesisHelper.streamName,
                Data: new util_1.TextEncoder().encode(JSON.stringify(payload)),
                PartitionKey: payload._id,
            });
            return kinesis.send(command);
        });
    }
    static fetchApiData() {
        return __awaiter(this, void 0, void 0, function* () {
            const response = yield axios_1.default.get(this.apiUrl, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                },
            });
            // Assume que a resposta é um array ou tem uma propriedade 'data' com array
            return Array.isArray(response.data) ? response.data : response.data.data || [];
        });
    }
    static processAndSendData() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                console.log('Buscando dados da API...');
                const apiData = yield this.fetchApiData();
                console.log(`Processando ${apiData.length} registros...`);
                for (const item of apiData) {
                    yield this.putRecord({
                        fullDocument: item,
                        collection: 'api_data',
                        operationType: 'insert',
                    });
                }
                console.log('Processamento concluído!');
            }
            catch (error) {
                console.error('Erro:', error);
            }
        });
    }
}
exports.ApiKinesisHelper = ApiKinesisHelper;
ApiKinesisHelper.streamName = process.env.KINESIS_STREAM_NAME;
ApiKinesisHelper.apiUrl = process.env.API_URL;
ApiKinesisHelper.apiKey = process.env.API_KEY;
// Para executar
// ApiKinesisHelper.processAndSendData();

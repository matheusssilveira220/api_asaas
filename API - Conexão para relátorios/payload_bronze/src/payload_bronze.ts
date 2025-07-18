import { KinesisClient, PutRecordCommand } from '@aws-sdk/client-kinesis';
import { TextEncoder } from 'util';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import * as dotenv from 'dotenv';

dotenv.config();

interface IKinesis<T> {
    fullDocument: T;
    collection: string;
    operationType: string;
}

interface IDataBricks<T> {
    _id: string;
    documentKey: string;
    fullDocument: T;
    operationType: string;
    updateDescription: any;
    ns: {
        db: string;
        coll: string;
    };
}

enum IDatabricksDb {
    BOT = 'bot'
}

const kinesis = new KinesisClient({
    region: 'us-east-1',
});

export class KinesisHelper {
    private static streamName = process.env.KINESIS_STREAM_NAME;

    private static data<U>(item: any): IDataBricks<U> {
        return {
            _id: item.id,
            documentKey: item.id,
            fullDocument: item.fullDocument,
            operationType: item.operationType,
            updateDescription: null,
            ns: {
                db: IDatabricksDb.BOT,
                coll: item.collection,
            },
        };
    }

    static async putRecord<T>(item: IKinesis<T>) {
        const payload = KinesisHelper.data<T>({ id: uuidv4(), ...item });
        const command = new PutRecordCommand({
            StreamName: KinesisHelper.streamName,
            Data: new TextEncoder().encode(JSON.stringify(payload)),
            PartitionKey: payload._id,
        });
        return kinesis.send(command);
    }
}

export class ApiProcessor {
    private static apiUrl = process.env.API_URL;
    private static apiKey = process.env.API_KEY;

    static async fetchApiData(): Promise<any[]> {
        if (!this.apiUrl) {
            throw new Error('API_URL não configurada no .env');
        }
        
        const response = await axios.get(this.apiUrl, {
            headers: {
                'access_token': this.apiKey,
                'Content-Type': 'application/json',
            },
        });
        
        return Array.isArray(response.data) ? response.data : response.data.data || [];
    }

    static async processAndSendData(): Promise<void> {
        try {
            console.log('Buscando dados da API...');
            const apiData = await this.fetchApiData();
            
            console.log(`Processando ${apiData.length} registros...`);
            
            for (const item of apiData) {
                await KinesisHelper.putRecord({
                    fullDocument: item,
                    collection: 'api_data',
                    operationType: 'insert',
                });
            }
            
            console.log('Processamento concluído!');
        } catch (error: any) {
            console.error('Erro:', error);
        }
    }
}

ApiProcessor.processAndSendData();
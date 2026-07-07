/**
 * Crop domain schema
 * Shared across roadmap, prediction, and analytics
 */

  $id: "Crop",
  type: "object",
  required: ["id", "name", "durationDays"],
  additionalProperties: false,
  properties: {
    id: {
      type: "string",
      description: "Unique crop identifier"
    },
    name: {
      type: "string",
      description: "Human readable crop name"
    },
    durationDays: {
      type: "number",
      description: "Total crop lifecycle in days"
    },
    scientificName: {
      type: "string",
      description: "Optional scientific crop name"
    },
    preferredSoilTypes: {
      type: "array",
      description: "Optional list of suitable soil types",
      items: {
        type: "string"
      }
    },
    optimalPhRange: {
      type: "object",
      description: "Optional pH range for ideal growth",
      required: ["min", "max"],
      additionalProperties: false,
      properties: {
        min: {
          type: "number"
        },
        max: {
          type: "number"
        }
      }
    }
  }
};

/**
 * Fertilizer recommendation schema
 */

  $id: "FertilizerRecommendationInput",
  type: "object",
  required: [
    "temperature",
    "humidity",
    "moisture",
    "soilType",
    "cropType",
    "nitrogen",
    "phosphorous",
    "potassium"
  ],
  additionalProperties: false,
  properties: {
    temperature: {
      type: "number",
      description: "Ambient temperature in degrees Celsius"
    },
    humidity: {
      type: "number",
      description: "Relative humidity percentage"
    },
    moisture: {
      type: "number",
      description: "Soil moisture percentage"
    },
    soilType: {
      type: "string",
      description: "Categorical soil type"
    },
    cropType: {
      type: "string",
      description: "Categorical crop type"
    },
    nitrogen: {
      type: "number",
      description: "Nitrogen content"
    },
    phosphorous: {
      type: "number",
      description: "Phosphorous content"
    },
    potassium: {
      type: "number",
      description: "Potassium content"
    }
  }
};

  $id: "FertilizerRecommendation",
  type: "object",
  required: ["fertilizerName", "confidence", "inputs"],
  additionalProperties: false,
  properties: {
    fertilizerName: {
      type: "string",
      description: "Recommended fertilizer label"
    },
    confidence: {
      type: "number",
      description: "Prediction confidence score (0-1)"
    },
    inputs: FertilizerRecommendationInputSchema,
    modelVersion: {
      type: "string",
      description: "Version of the fertilizer recommendation model"
    },
    createdAt: {
      type: "string",
      description: "ISO timestamp when the recommendation was generated"
    }
  }
};

/**
 * Growth stage schema
 */

  $id: "GrowthStage",
  type: "object",
  required: ["name", "startDay", "endDay"],
  additionalProperties: false,
  properties: {
    name: {
      type: "string",
      description: "Stage name (e.g., Germination)"
    },
    startDay: {
      type: "number",
      description: "Start day of stage"
    },
    endDay: {
      type: "number",
      description: "End day of stage"
    },
    cropId: {
      type: "string",
      description: "Crop identifier that owns this stage"
    },
    description: {
      type: "string",
      description: "Optional stage description"
    },
    recommendedActions: {
      type: "array",
      description: "Suggested actions during this stage",
      items: {
        type: "string"
      }
    }
  }
};

/**
 * Prediction output schema
 */

  $id: "PredictionResult",
  type: "object",
  required: ["predictionType", "confidence", "result"],
  additionalProperties: false,
  properties: {
    predictionType: {
      type: "string",
      description: "Type of prediction returned by the model"
    },
    confidence: {
      type: "number",
      description: "Model confidence score (0-1)"
    },
    result: {
      description: "Prediction outcome",
      oneOf: [
        { type: "string" },
        { type: "number" },
        { type: "boolean" },
        { type: "object" },
        { type: "array" },
        { type: "null" }
      ]
    },
    inputs: {
      type: "object",
      description: "Input payload used to produce the prediction"
    },
    metadata: {
      type: "object",
      description: "Optional explanatory metadata returned by the model"
    },
    modelVersion: {
      type: "string",
      description: "Version of the model that produced the result"
    },
    createdAt: {
      type: "string",
      description: "ISO timestamp when the prediction was generated"
    }
  }
};

/**
 * Soil data schema
 */

  $id: "SoilData",
  type: "object",
  required: ["n", "p", "k"],
  additionalProperties: false,
  properties: {
    n: {
      type: "number",
      description: "Nitrogen level"
    },
    p: {
      type: "number",
      description: "Phosphorus level"
    },
    k: {
      type: "number",
      description: "Potassium level"
    },
    ph: {
      type: "number",
      description: "Soil pH value"
    },
    moisture: {
      type: "number",
      description: "Soil moisture percentage"
    },
    temperature: {
      type: "number",
      description: "Soil temperature"
    },
    collectedAt: {
      type: "string",
      description: "ISO timestamp when the soil sample was collected"
    },
    source: {
      type: "string",
      description: "Origin of the soil data, such as sensor or manual input"
    }
  }
};

  CropSchema,
  FertilizerRecommendationInputSchema,
  FertilizerRecommendationSchema,
  GrowthStageSchema,
  PredictionResultSchema,
  SoilDataSchema
} from "./index.js";

const schemaMap = {
  Crop: CropSchema,
  FertilizerRecommendationInput: FertilizerRecommendationInputSchema,
  FertilizerRecommendation: FertilizerRecommendationSchema,
  GrowthStage: GrowthStageSchema,
  PredictionResult: PredictionResultSchema,
  SoilData: SoilDataSchema
};

const validatorCache = new Map();

function validateValue(schema, value, path = "value") {
  if (!schema) {
    return [`Unknown schema at ${path}`];
  }

  if (schema.oneOf) {
    const branchErrors = schema.oneOf.some((optionSchema) => validateValue(optionSchema, value, path).length === 0);
    return branchErrors ? [] : [`${path} does not match any allowed schema branch`];
  }

  if (schema.anyOf) {
    const branchErrors = schema.anyOf.some((optionSchema) => validateValue(optionSchema, value, path).length === 0);
    return branchErrors ? [] : [`${path} does not match any allowed schema branch`];
  }

  if (schema.type) {
    const allowedTypes = Array.isArray(schema.type) ? schema.type : [schema.type];
    const actualType = Array.isArray(value) ? "array" : value === null ? "null" : typeof value;
    if (!allowedTypes.includes(actualType)) {
      return [`${path} must be of type ${allowedTypes.join(" or ")}`];
    }
  }

  if (schema.enum && !schema.enum.includes(value)) {
    return [`${path} must be one of: ${schema.enum.join(", ")}`];
  }

  if (schema.type === "array") {
    const items = schema.items || {};
    const itemErrors = [];
    value.forEach((item, index) => {
      itemErrors.push(...validateValue(items, item, `${path}[${index}]`));
    });
    return itemErrors;
  }

  if (schema.type === "object") {
    if (typeof value !== "object" || value === null || Array.isArray(value)) {
      return [`${path} must be an object`];
    }

    const errors = [];
    const required = schema.required || [];
    required.forEach((key) => {
      if (!(key in value)) {
        errors.push(`${path}.${key} is required`);
      }
    });

    const properties = schema.properties || {};
    Object.entries(properties).forEach(([key, propertySchema]) => {
      if (key in value) {
        errors.push(...validateValue(propertySchema, value[key], `${path}.${key}`));
      }
    });

    if (schema.additionalProperties === false) {
      Object.keys(value).forEach((key) => {
        if (!(key in properties)) {
          errors.push(`${path}.${key} is not allowed`);
        }
      });
    }

    return errors;
  }

  return [];
}

  const errors = validateValue(schema, data);

  return {
    valid: errors.length === 0,
    errors
  };
}

  const schema = schemaMap[schemaName];

  if (!schema) {
    return {
      valid: false,
      errors: [`Unknown domain schema: ${schemaName}`]
    };
  }

  if (!validatorCache.has(schemaName)) {
    validatorCache.set(schemaName, (value) => validateSchema(schema, value));
  }

  return validatorCache.get(schemaName)(data);
}



const DomainSchemas = {
  Crop: CropSchema,
  FertilizerRecommendationInput: FertilizerRecommendationInputSchema,
  FertilizerRecommendation: FertilizerRecommendationSchema,
  GrowthStage: GrowthStageSchema,
  PredictionResult: PredictionResultSchema,
  SoilData: SoilDataSchema
};

if (typeof window !== 'undefined') {
  window.AgriTechDomain = {
    ...DomainSchemas,
    validateSchema,
    validateDomainData
  };
}

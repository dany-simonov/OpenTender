import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import {
  DocumentIcon,
  ClockIcon,
  UserIcon,
  CurrencyDollarIcon,
  TagIcon,
  CalendarIcon,
  ExclamationIcon,
} from '@heroicons/react/outline';

export default function TenderDetail() {
  const { id } = useParams();
  const [tender, setTender] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('info');

  useEffect(() => {
    fetchTenderDetails();
  }, [id]);

  const fetchTenderDetails = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/tenders/${id}`);
      setTender(response.data);
    } catch (err) {
      setError('Ошибка при загрузке данных тендера');
      console.error('Error fetching tender details:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
    }).format(price);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!tender) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Тендер не найден</p>
      </div>
    );
  }

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="md:flex md:items-center md:justify-between">
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              {tender.title}
            </h2>
          </div>
          <div className="mt-4 flex md:mt-0 md:ml-4">
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                tender.status === 'active'
                  ? 'bg-green-100 text-green-800'
                  : tender.status === 'completed'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {tender.status === 'active'
                ? 'Активный'
                : tender.status === 'completed'
                ? 'Завершен'
                : 'Отменен'}
            </span>
          </div>
        </div>

        <div className="mt-6">
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div className="flex items-center">
                  <CurrencyDollarIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Начальная цена</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatPrice(tender.price)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center">
                  <CalendarIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Срок подачи</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatDate(tender.submission_deadline)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center">
                  <TagIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Категория</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {tender.category}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200">
              <nav className="flex -mb-px">
                <button
                  onClick={() => setActiveTab('info')}
                  className={`${
                    activeTab === 'info'
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
                >
                  Информация
                </button>
                <button
                  onClick={() => setActiveTab('documents')}
                  className={`${
                    activeTab === 'documents'
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
                >
                  Документы
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`${
                    activeTab === 'history'
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm`}
                >
                  История изменений
                </button>
              </nav>
            </div>

            <div className="px-4 py-5 sm:p-6">
              {activeTab === 'info' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Описание
                    </h3>
                    <div className="mt-2 text-sm text-gray-500">
                      {tender.description}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Требования
                    </h3>
                    <div className="mt-2 text-sm text-gray-500">
                      <ul className="list-disc pl-5 space-y-2">
                        {tender.requirements?.map((req, index) => (
                          <li key={index}>{req}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Заказчик
                    </h3>
                    <div className="mt-2 text-sm text-gray-500">
                      <p>{tender.customer.name}</p>
                      <p>{tender.customer.inn}</p>
                      <p>{tender.customer.address}</p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'documents' && (
                <div className="space-y-4">
                  {tender.documents?.map((doc, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center">
                        <DocumentIcon className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {doc.name}
                          </p>
                          <p className="text-sm text-gray-500">
                            {doc.size} • {doc.type}
                          </p>
                        </div>
                      </div>
                      <a
                        href={doc.url}
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200"
                      >
                        Скачать
                      </a>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'history' && (
                <div className="flow-root">
                  <ul className="-mb-8">
                    {tender.history?.map((event, index) => (
                      <li key={index}>
                        <div className="relative pb-8">
                          {index !== tender.history.length - 1 && (
                            <span
                              className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                              aria-hidden="true"
                            />
                          )}
                          <div className="relative flex space-x-3">
                            <div>
                              <span
                                className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                                  event.type === 'status'
                                    ? 'bg-blue-500'
                                    : event.type === 'price'
                                    ? 'bg-green-500'
                                    : 'bg-gray-500'
                                }`}
                              >
                                <ClockIcon
                                  className="h-5 w-5 text-white"
                                  aria-hidden="true"
                                />
                              </span>
                            </div>
                            <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                              <div>
                                <p className="text-sm text-gray-500">
                                  {event.description}
                                </p>
                              </div>
                              <div className="text-right text-sm whitespace-nowrap text-gray-500">
                                <time dateTime={event.date}>
                                  {formatDate(event.date)}
                                </time>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>

        {tender.status === 'active' && (
          <div className="mt-6">
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <ExclamationIcon
                    className="h-5 w-5 text-yellow-400"
                    aria-hidden="true"
                  />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    Тендер активен. У вас есть время до{' '}
                    {formatDate(tender.submission_deadline)} для подачи заявки.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 
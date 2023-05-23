using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;
using Npgsql;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;

namespace ServerEspCam
{
    internal class Program
    {
        static void Main(string[] args)
        {
            MqttClient mqtt = new MqttClient("test.mosquitto.org");

            string[] subscribe = new string[1];
            subscribe[0] = "Esp32_FaceWebServer";

            mqtt.MqttMsgPublishReceived += MqttClient_MqttMsgPublishReceived;

            byte[] bytes = new byte[1];

            mqtt.Subscribe(subscribe, new byte[] { MqttMsgBase.QOS_LEVEL_AT_LEAST_ONCE });
            mqtt.Connect("8402d29a-e588-4b60-b687-947785a1b8ce");
            while (mqtt.IsConnected)
            {
                

            }

            TestConnection();
        }

        private static void InsertSql(string Message)
        {
            using(NpgsqlConnection connection = GetConnection())
            {
                connection.Open();

                string[] insertData = Message.Split(';');
                if (insertData.Length > 1)
                {
                    string query = "INSERT INTO public.iotespcam(name, email) VALUES (@Name," +
                        " @Email);";

                    using (NpgsqlCommand command = new NpgsqlCommand(query, connection))
                    {
                        Console.WriteLine(insertData[0]);
                        command.Parameters.AddWithValue("@Name", insertData[0]);
                        Console.WriteLine(insertData[1]);
                        command.Parameters.AddWithValue("@Email", insertData[1]);

                       command.ExecuteNonQuery();
                    }
                }
            }
        }
        private static void TestConnection()
        {
            using (NpgsqlConnection connection = GetConnection())
            {
                    try
                    {
                        connection.Open();
                        if (connection.State == ConnectionState.Open)
                        {
                            Console.WriteLine("Connected");
                        }
                    }
                    catch
                    {
                        Console.WriteLine("Not Connected");
                    }
                }
            }
        private static NpgsqlConnection GetConnection()
        {
            return new NpgsqlConnection(@"Server=localhost;Port=5432;User Id=postgres;Password=2510;Database=IotEspCam");
        }

        private static void MqttClient_MqttMsgPublishReceived(object sender, uPLibrary.Networking.M2Mqtt.Messages.MqttMsgPublishEventArgs e)
        {
            var message = Encoding.UTF8.GetString(e.Message);
            Console.WriteLine(message);
            InsertSql(message);
        }
    }

}
